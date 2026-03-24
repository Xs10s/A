<?php
/**
 * REST API: compute, save, my, download, register, login.
 *
 * @package LJLK_Horoscoop
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class LJLK_Horoscoop_REST {

	const NAMESPACE = 'ljlk/v1';

	public static function register_routes() {
		register_rest_route( self::NAMESPACE, '/compute', array(
			'methods'             => 'POST',
			'callback'            => array( __CLASS__, 'compute' ),
			'permission_callback' => '__return_true',
			'args'                => self::compute_args(),
		) );
		register_rest_route( self::NAMESPACE, '/save', array(
			'methods'             => 'POST',
			'callback'            => array( __CLASS__, 'save' ),
			'permission_callback' => array( __CLASS__, 'check_logged_in' ),
			'args'                => self::save_args(),
		) );
		register_rest_route( self::NAMESPACE, '/my', array(
			'methods'             => 'GET',
			'callback'            => array( __CLASS__, 'my' ),
			'permission_callback' => array( __CLASS__, 'check_logged_in' ),
		) );
		register_rest_route( self::NAMESPACE, '/download/json', array(
			'methods'             => 'GET',
			'callback'            => array( __CLASS__, 'download_json' ),
			'permission_callback' => array( __CLASS__, 'check_logged_in' ),
			'args'                => array( 'run_id' => array( 'required' => true, 'type' => 'integer', 'sanitize_callback' => 'absint' ) ),
		) );
		register_rest_route( self::NAMESPACE, '/download/wheel.svg', array(
			'methods'             => 'GET',
			'callback'            => array( __CLASS__, 'download_wheel' ),
			'permission_callback' => array( __CLASS__, 'check_logged_in' ),
			'args'                => array( 'run_id' => array( 'required' => true, 'type' => 'integer', 'sanitize_callback' => 'absint' ) ),
		) );
		register_rest_route( self::NAMESPACE, '/download/report.pdf', array(
			'methods'             => 'GET',
			'callback'            => array( __CLASS__, 'download_report' ),
			'permission_callback' => array( __CLASS__, 'check_logged_in' ),
			'args'                => array( 'run_id' => array( 'required' => true, 'type' => 'integer', 'sanitize_callback' => 'absint' ) ),
		) );
		register_rest_route( self::NAMESPACE, '/register', array(
			'methods'             => 'POST',
			'callback'            => array( __CLASS__, 'register' ),
			'permission_callback' => '__return_true',
			'args'                => self::register_args(),
		) );
		register_rest_route( self::NAMESPACE, '/login', array(
			'methods'             => 'POST',
			'callback'            => array( __CLASS__, 'login' ),
			'permission_callback' => '__return_true',
			'args'                => self::login_args(),
		) );
	}

	private static function compute_args() {
		return array(
			'birth_date'          => array( 'required' => true, 'type' => 'string', 'validate_callback' => function( $v ) { return ljlk_horoscoop_validate_birth_date( $v ); } ),
			'birth_time'          => array( 'type' => 'string', 'validate_callback' => function( $v ) { return ljlk_horoscoop_validate_birth_time( $v ); } ),
			'latitude'            => array( 'type' => 'number' ),
			'longitude'           => array( 'type' => 'number' ),
			'timezone_iana'       => array( 'type' => 'string' ),
			'utc_offset_minutes'  => array( 'type' => 'integer' ),
			'settings'            => array( 'type' => 'object' ),
		);
	}

	private static function save_args() {
		$args = self::compute_args();
		$args['label']   = array( 'type' => 'string' );
		$args['horoscoop'] = array( 'type' => 'object' ); // optional precomputed; verified by hash
		return $args;
	}

	private static function register_args() {
		return array(
			'email'    => array( 'required' => true, 'type' => 'string', 'format' => 'email' ),
			'password' => array( 'required' => true, 'type' => 'string', 'minLength' => 10 ),
		);
	}

	private static function login_args() {
		return array(
			'email'    => array( 'required' => true, 'type' => 'string' ),
			'password' => array( 'required' => true, 'type' => 'string' ),
		);
	}

	public static function check_logged_in( WP_REST_Request $request ) {
		return is_user_logged_in();
	}

	/**
	 * Serve raw SVG/PDF response body so REST server does not JSON-encode it.
	 *
	 * @param bool             $served  Whether the request has already been served.
	 * @param WP_HTTP_Response $result  Response object.
	 * @param WP_REST_Request  $request Request object.
	 * @param WP_REST_Server   $server  Server instance.
	 * @return bool True if we served the request.
	 */
	public static function serve_raw_download( $served, $result, $request, $server ) {
		$route = $request->get_route();
		if ( strpos( $route, '/' . self::NAMESPACE . '/download/' ) === false ) {
			return $served;
		}
		$data = $result->get_data();
		if ( ! is_string( $data ) || $result->get_status() >= 400 ) {
			return $served;
		}
		foreach ( $result->get_headers() as $key => $value ) {
			header( $key . ': ' . $value );
		}
		header( 'Content-Length: ' . strlen( $data ) );
		echo $data; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- raw binary/SVG output
		exit;
	}

	/**
	 * POST /compute — public, rate limited.
	 */
	public static function compute( WP_REST_Request $request ) {
		$ip = LJLK_Horoscoop_Auth::get_client_ip();
		if ( ! LJLK_Horoscoop_Auth::compute_rate_limit_ok( $ip ) ) {
			return new WP_REST_Response( array( 'code' => 'rate_limit', 'message' => __( 'Te veel verzoeken. Probeer het later opnieuw.', 'ljlk-horoscoop' ) ), 429 );
		}
		$base = get_option( 'ljlk_horoscoop_api_base_url', '' );
		if ( empty( $base ) ) {
			return new WP_REST_Response( array( 'code' => 'config', 'message' => __( 'API is niet geconfigureerd.', 'ljlk-horoscoop' ) ), 503 );
		}
		$params = $request->get_json_params() ?: $request->get_body_params();
		$birth_date = isset( $params['birth_date'] ) ? sanitize_text_field( $params['birth_date'] ) : '';
		if ( ! ljlk_horoscoop_validate_birth_date( $birth_date ) ) {
			return new WP_REST_Response( array( 'code' => 'invalid_input', 'message' => __( 'Ongeldige geboortedatum (gebruik JJJJ-MM-DD).', 'ljlk-horoscoop' ) ), 400 );
		}
		if ( ! empty( $params['birth_time'] ) && ! ljlk_horoscoop_validate_birth_time( $params['birth_time'] ) ) {
			return new WP_REST_Response( array( 'code' => 'invalid_input', 'message' => __( 'Ongeldige geboortetijd.', 'ljlk-horoscoop' ) ), 400 );
		}
		$payload = ljlk_horoscoop_sanitize_for_api( $params );
		$payload['birth_date'] = substr( $birth_date, 0, 10 );
		$result = LJLK_Horoscoop_Client::compute( $base, $payload );
		if ( is_wp_error( $result ) ) {
			$msg = $result->get_error_message();
			return new WP_REST_Response( array( 'code' => 'api_error', 'message' => $msg ), 502 );
		}
		return rest_ensure_response( $result );
	}

	/**
	 * POST /save — create/update profile and run; auth required.
	 */
	public static function save( WP_REST_Request $request ) {
		$user_id = get_current_user_id();
		if ( ! $user_id ) {
			return new WP_REST_Response( array( 'code' => 'unauthorized', 'message' => __( 'Log in om op te slaan.', 'ljlk-horoscoop' ) ), 401 );
		}
		$params = $request->get_json_params() ?: $request->get_body_params();
		$birth_date = isset( $params['birth_date'] ) ? sanitize_text_field( $params['birth_date'] ) : '';
		if ( ! ljlk_horoscoop_validate_birth_date( $birth_date ) ) {
			return new WP_REST_Response( array( 'code' => 'invalid_input', 'message' => __( 'Ongeldige geboortedatum.', 'ljlk-horoscoop' ) ), 400 );
		}
		$payload = ljlk_horoscoop_sanitize_for_api( $params );
		$payload['birth_date'] = substr( $birth_date, 0, 10 );
		if ( ! empty( $params['birth_time'] ) ) {
			$payload['birth_time'] = sanitize_text_field( $params['birth_time'] );
		}
		$label = isset( $params['label'] ) ? sanitize_text_field( $params['label'] ) : 'Mijn horoscoop';
		if ( strlen( $label ) > 100 ) {
			$label = substr( $label, 0, 100 );
		}
		$max_saves = (int) get_option( 'ljlk_horoscoop_max_saves_per_user', 10 );
		global $wpdb;
		$profiles_table = LJLK_Horoscoop_DB::profiles_table();
		$runs_table     = LJLK_Horoscoop_DB::runs_table();
		$profile_id = $wpdb->get_var( $wpdb->prepare(
			"SELECT id FROM {$profiles_table} WHERE user_id = %d ORDER BY id ASC LIMIT 1",
			$user_id
		) );
		if ( ! $profile_id ) {
			$total_profiles = (int) $wpdb->get_var( $wpdb->prepare( "SELECT COUNT(*) FROM {$profiles_table} WHERE user_id = %d", $user_id ) );
			if ( $total_profiles >= max( 1, $max_saves ) ) {
				return new WP_REST_Response( array( 'code' => 'limit', 'message' => __( 'Maximum aantal horoscopen bereikt.', 'ljlk-horoscoop' ) ), 403 );
			}
			$wpdb->insert(
				$profiles_table,
				array(
					'user_id'           => $user_id,
					'label'             => $label,
					'birth_date'        => $payload['birth_date'],
					'birth_time'        => ! empty( $payload['birth_time_local'] ) ? $payload['birth_time_local'] : null,
					'latitude'          => $payload['lat'],
					'longitude'         => $payload['lon'],
					'timezone_iana'     => $payload['timezone_iana'],
					'utc_offset_minutes'=> $payload['utc_offset_minutes'],
					'settings_json'     => isset( $payload['settings'] ) ? wp_json_encode( $payload['settings'] ) : null,
					'created_at'        => current_time( 'mysql' ),
				),
				array( '%d', '%s', '%s', '%s', '%f', '%f', '%s', '%d', '%s', '%s' )
			);
			$profile_id = $wpdb->insert_id;
		}
		$hash_payload = array_merge( $params, array( 'birth_date' => $payload['birth_date'] ) );
		if ( ! empty( $params['birth_time'] ) ) {
			$hash_payload['birth_time'] = $params['birth_time'];
		}
		$input_hash = ljlk_horoscoop_input_hash( $hash_payload );
		$existing_run = $wpdb->get_row( $wpdb->prepare(
			"SELECT id, computed_at FROM {$runs_table} WHERE profile_id = %d AND input_hash = %s",
			$profile_id,
			$input_hash
		), ARRAY_A );
		if ( $existing_run ) {
			return rest_ensure_response( array(
				'profile_id'  => (int) $profile_id,
				'run_id'      => (int) $existing_run['id'],
				'computed_at' => $existing_run['computed_at'],
			) );
		}
		$horoscoop = isset( $params['horoscoop'] ) && is_array( $params['horoscoop'] ) ? $params['horoscoop'] : null;
		$base = get_option( 'ljlk_horoscoop_api_base_url', '' );
		if ( ! $horoscoop && ! empty( $base ) ) {
			$horoscoop = LJLK_Horoscoop_Client::compute( $base, $payload );
			if ( is_wp_error( $horoscoop ) ) {
				return new WP_REST_Response( array( 'code' => 'api_error', 'message' => $horoscoop->get_error_message() ), 502 );
			}
		}
		if ( ! $horoscoop || ! is_array( $horoscoop ) ) {
			return new WP_REST_Response( array( 'code' => 'invalid_input', 'message' => __( 'Geen horoscoop om op te slaan. Bereken eerst een horoscoop.', 'ljlk-horoscoop' ) ), 400 );
		}
		$total_runs = (int) $wpdb->get_var( $wpdb->prepare( "SELECT COUNT(*) FROM {$runs_table} r INNER JOIN {$profiles_table} p ON r.profile_id = p.id WHERE p.user_id = %d", $user_id ) );
		if ( $total_runs >= max( 1, $max_saves ) * 5 ) {
			return new WP_REST_Response( array( 'code' => 'limit', 'message' => __( 'Maximum aantal runs bereikt.', 'ljlk-horoscoop' ) ), 403 );
		}
		$wheel_svg = null;
		$report_pdf = null;
		$cache_svg_pdf = get_option( 'ljlk_horoscoop_cache_svg_pdf', false );
		if ( $cache_svg_pdf && ! empty( $base ) ) {
			$svg_result = LJLK_Horoscoop_Client::render_wheel_svg( $base, array( 'engine_json' => $horoscoop ) );
			if ( ! is_wp_error( $svg_result ) ) {
				$wheel_svg = $svg_result;
			}
			$pdf_result = LJLK_Horoscoop_Client::render_report_pdf( $base, array( 'engine_json' => $horoscoop ) );
			if ( ! is_wp_error( $pdf_result ) && strlen( $pdf_result ) < 5 * 1024 * 1024 ) {
				$report_pdf = $pdf_result;
			}
		}
		$wpdb->insert(
			$runs_table,
			array(
				'profile_id'     => $profile_id,
				'input_hash'     => $input_hash,
				'engine_version' => null,
				'computed_at'    => current_time( 'mysql' ),
				'horoscoop_json' => wp_json_encode( $horoscoop ),
				'wheel_svg'      => $wheel_svg,
				'report_pdf'     => $report_pdf,
				'report_pdf_url' => null,
			),
			array( '%d', '%s', '%s', '%s', '%s', '%s', '%s', '%s' )
		);
		$run_id = $wpdb->insert_id;
		return rest_ensure_response( array(
			'profile_id'  => (int) $profile_id,
			'run_id'      => (int) $run_id,
			'computed_at' => current_time( 'mysql' ),
		) );
	}

	/**
	 * GET /my — list profiles and runs for current user.
	 */
	public static function my( WP_REST_Request $request ) {
		$user_id = get_current_user_id();
		global $wpdb;
		$profiles_table = LJLK_Horoscoop_DB::profiles_table();
		$runs_table     = LJLK_Horoscoop_DB::runs_table();
		$profiles = $wpdb->get_results( $wpdb->prepare(
			"SELECT id, label, birth_date, birth_time, created_at FROM {$profiles_table} WHERE user_id = %d ORDER BY id",
			$user_id
		), ARRAY_A );
		$out = array();
		foreach ( $profiles as $p ) {
			$runs = $wpdb->get_results( $wpdb->prepare(
				"SELECT id, input_hash, computed_at, horoscoop_json, wheel_svg, report_pdf, report_pdf_url FROM {$runs_table} WHERE profile_id = %d ORDER BY computed_at DESC",
				$p['id']
			), ARRAY_A );
			$runs_out = array();
			foreach ( $runs as $r ) {
				$runs_out[] = array(
					'run_id'      => (int) $r['id'],
					'computed_at' => $r['computed_at'],
					'has_svg'     => ! empty( $r['wheel_svg'] ),
					'has_pdf'     => ! empty( $r['report_pdf'] ) || ! empty( $r['report_pdf_url'] ),
				);
			}
			$out[] = array(
				'profile_id'   => (int) $p['id'],
				'label'        => $p['label'],
				'birth_date'   => $p['birth_date'],
				'birth_time'   => $p['birth_time'],
				'created_at'   => $p['created_at'],
				'runs'         => $runs_out,
			);
		}
		return rest_ensure_response( array( 'profiles' => $out ) );
	}

	private static function get_run_and_check_ownership( $run_id ) {
		$user_id = get_current_user_id();
		global $wpdb;
		$profiles_table = LJLK_Horoscoop_DB::profiles_table();
		$runs_table     = LJLK_Horoscoop_DB::runs_table();
		$run = $wpdb->get_row( $wpdb->prepare(
			"SELECT r.* FROM {$runs_table} r INNER JOIN {$profiles_table} p ON r.profile_id = p.id WHERE r.id = %d AND p.user_id = %d",
			$run_id,
			$user_id
		), ARRAY_A );
		return $run;
	}

	public static function download_json( WP_REST_Request $request ) {
		$run_id = (int) $request['run_id'];
		$run = self::get_run_and_check_ownership( $run_id );
		if ( ! $run ) {
			return new WP_REST_Response( array( 'code' => 'not_found' ), 404 );
		}
		$decoded = json_decode( $run['horoscoop_json'], true );
		$response = new WP_REST_Response( $decoded, 200 );
		$response->header( 'Content-Disposition', 'attachment; filename="horoscoop-' . $run_id . '.json"' );
		return $response;
	}

	public static function download_wheel( WP_REST_Request $request ) {
		$run_id = (int) $request['run_id'];
		$run = self::get_run_and_check_ownership( $run_id );
		if ( ! $run || empty( $run['wheel_svg'] ) ) {
			return new WP_REST_Response( array( 'code' => 'not_found' ), 404 );
		}
		$response = new WP_REST_Response( $run['wheel_svg'], 200 );
		$response->header( 'Content-Type', 'image/svg+xml' );
		$response->header( 'Content-Disposition', 'inline; filename="wheel-' . $run_id . '.svg"' );
		return $response;
	}

	public static function download_report( WP_REST_Request $request ) {
		$run_id = (int) $request['run_id'];
		$run = self::get_run_and_check_ownership( $run_id );
		if ( ! $run ) {
			return new WP_REST_Response( array( 'code' => 'not_found' ), 404 );
		}
		if ( ! empty( $run['report_pdf'] ) ) {
			$response = new WP_REST_Response( $run['report_pdf'], 200 );
			$response->header( 'Content-Type', 'application/pdf' );
			$response->header( 'Content-Disposition', 'attachment; filename="report-' . $run_id . '.pdf"' );
			return $response;
		}
		if ( ! empty( $run['report_pdf_url'] ) ) {
			return new WP_REST_Response( null, 302, array( 'Location' => $run['report_pdf_url'] ) );
		}
		return new WP_REST_Response( array( 'code' => 'not_found' ), 404 );
	}

	/**
	 * POST /register — email + password only; create user and log in.
	 */
	public static function register( WP_REST_Request $request ) {
		$ip = LJLK_Horoscoop_Auth::get_client_ip();
		if ( ! LJLK_Horoscoop_Auth::register_throttle_ok( $ip, 5 ) ) {
			return new WP_REST_Response( array( 'code' => 'throttle', 'message' => __( 'Te veel registratiepogingen. Probeer het later opnieuw.', 'ljlk-horoscoop' ) ), 429 );
		}
		$params = $request->get_json_params() ?: $request->get_body_params();
		$email = isset( $params['email'] ) ? sanitize_email( $params['email'] ) : '';
		$password = isset( $params['password'] ) ? $params['password'] : '';
		if ( ! is_email( $email ) ) {
			return new WP_REST_Response( array( 'code' => 'invalid_email', 'message' => __( 'Ongeldig e-mailadres.', 'ljlk-horoscoop' ) ), 400 );
		}
		if ( strlen( $password ) < 10 ) {
			return new WP_REST_Response( array( 'code' => 'weak_password', 'message' => __( 'Wachtwoord moet minimaal 10 tekens zijn.', 'ljlk-horoscoop' ) ), 400 );
		}
		if ( email_exists( $email ) ) {
			return new WP_REST_Response( array( 'code' => 'email_exists', 'message' => __( 'Dit e-mailadres is al geregistreerd. Log in.', 'ljlk-horoscoop' ) ), 400 );
		}
		$username = sanitize_user( str_replace( array( '@', '.', '+', ' ' ), array( '_', '_', '_', '_' ), $email ), true );
		if ( strlen( $username ) < 2 ) {
			$username = 'user_' . wp_rand( 10000, 99999 );
		}
		if ( username_exists( $username ) ) {
			$username = $username . '_' . wp_rand( 100, 999 );
		}
		$user_id = wp_create_user( $username, $password, $email );
		if ( is_wp_error( $user_id ) ) {
			return new WP_REST_Response( array( 'code' => 'creation_failed', 'message' => $user_id->get_error_message() ), 400 );
		}
		wp_set_auth_cookie( $user_id, true );
		wp_set_current_user( $user_id );
		return rest_ensure_response( array( 'success' => true, 'user_id' => $user_id ) );
	}

	/**
	 * POST /login — email + password; verify and set auth cookie.
	 */
	public static function login( WP_REST_Request $request ) {
		$params = $request->get_json_params() ?: $request->get_body_params();
		$email = isset( $params['email'] ) ? sanitize_email( $params['email'] ) : '';
		$password = isset( $params['password'] ) ? $params['password'] : '';
		if ( ! is_email( $email ) ) {
			return new WP_REST_Response( array( 'code' => 'invalid_email', 'message' => __( 'Ongeldig e-mailadres.', 'ljlk-horoscoop' ) ), 400 );
		}
		$user = get_user_by( 'email', $email );
		if ( ! $user || ! wp_check_password( $password, $user->user_pass, $user->ID ) ) {
			return new WP_REST_Response( array( 'code' => 'invalid_credentials', 'message' => __( 'Onjuist e-mailadres of wachtwoord.', 'ljlk-horoscoop' ) ), 401 );
		}
		wp_set_auth_cookie( $user->ID, true );
		wp_set_current_user( $user->ID );
		return rest_ensure_response( array( 'success' => true, 'user_id' => $user->ID ) );
	}
}
