<?php
/**
 * HTTP client for Python Horoscoop API.
 *
 * @package LJLK_Horoscoop
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class LJLK_Horoscoop_Client {

	/**
	 * POST to /api/horoscoop and return decoded JSON or WP_Error.
	 *
	 * @param string $base_url Python API base URL (no trailing slash).
	 * @param array  $payload  Sanitized payload (birth_date, birth_time_local, lat, lon, etc.).
	 * @return array|WP_Error Decoded JSON or error.
	 */
	public static function compute( $base_url, array $payload ) {
		$url = rtrim( $base_url, '/' ) . '/api/horoscoop';
		$body = wp_json_encode( $payload );
		$resp = wp_remote_post(
			$url,
			array(
				'timeout' => 30,
				'headers' => array(
					'Content-Type' => 'application/json',
				),
				'body'    => $body,
			)
		);
		if ( is_wp_error( $resp ) ) {
			return $resp;
		}
		$code = wp_remote_retrieve_response_code( $resp );
		$body_raw = wp_remote_retrieve_body( $resp );
		if ( $code < 200 || $code >= 300 ) {
			return new WP_Error( 'api_error', __( 'Horoscoop-API antwoordde met een fout.', 'ljlk-horoscoop' ), array( 'status' => $code, 'body' => $body_raw ) );
		}
		$decoded = json_decode( $body_raw, true );
		if ( json_last_error() !== JSON_ERROR_NONE ) {
			return new WP_Error( 'invalid_json', __( 'Ongeldig antwoord van de API.', 'ljlk-horoscoop' ) );
		}
		return $decoded;
	}

	/**
	 * POST to /api/render/wheel.svg; body can be engine_json or birth params.
	 *
	 * @param string $base_url Python API base URL.
	 * @param array  $body     Either engine_json key with horoscoop dict, or birth_date + params.
	 * @return string|WP_Error SVG content or error.
	 */
	public static function render_wheel_svg( $base_url, array $body ) {
		$url = rtrim( $base_url, '/' ) . '/api/render/wheel.svg';
		$resp = wp_remote_post(
			$url,
			array(
				'timeout' => 45,
				'headers' => array( 'Content-Type' => 'application/json' ),
				'body'    => wp_json_encode( $body ),
			)
		);
		if ( is_wp_error( $resp ) ) {
			return $resp;
		}
		$code = wp_remote_retrieve_response_code( $resp );
		$content = wp_remote_retrieve_body( $resp );
		if ( $code < 200 || $code >= 300 ) {
			return new WP_Error( 'svg_error', __( 'SVG kon niet worden opgehaald.', 'ljlk-horoscoop' ), array( 'status' => $code ) );
		}
		return $content;
	}

	/**
	 * POST to /api/render/report.pdf; body can be engine_json or birth params.
	 *
	 * @param string $base_url Python API base URL.
	 * @param array  $body     Either engine_json or birth_date + params.
	 * @return string|WP_Error Binary PDF content or error.
	 */
	public static function render_report_pdf( $base_url, array $body ) {
		$url = rtrim( $base_url, '/' ) . '/api/render/report.pdf';
		$resp = wp_remote_post(
			$url,
			array(
				'timeout' => 60,
				'headers' => array( 'Content-Type' => 'application/json' ),
				'body'    => wp_json_encode( $body ),
			)
		);
		if ( is_wp_error( $resp ) ) {
			return $resp;
		}
		$code = wp_remote_retrieve_response_code( $resp );
		$content = wp_remote_retrieve_body( $resp );
		if ( $code < 200 || $code >= 300 ) {
			return new WP_Error( 'pdf_error', __( 'PDF kon niet worden opgehaald.', 'ljlk-horoscoop' ), array( 'status' => $code ) );
		}
		return $content;
	}
}
