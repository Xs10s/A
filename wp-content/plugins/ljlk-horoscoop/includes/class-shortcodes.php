<?php
/**
 * Shortcodes and admin settings for LJLK Horoscoop.
 *
 * @package LJLK_Horoscoop
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class LJLK_Horoscoop_Shortcodes {

	const APP_HANDLE = 'ljlk-horoscoop-app';
	const APP_SCRIPT = 'ljlk-horoscoop-app';
	const APP_STYLE  = 'ljlk-horoscoop-app';

	public static function enqueue_assets() {
		global $post;
		if ( ! is_a( $post, 'WP_Post' ) || ! has_shortcode( $post->post_content, 'ljlk_horoscoop_app' ) && ! has_shortcode( $post->post_content, 'ljlk_horoscoop_dashboard' ) ) {
			return;
		}
		$base = get_option( 'ljlk_horoscoop_api_base_url', '' );
		wp_enqueue_script(
			self::APP_SCRIPT,
			LJLK_HOROSCOOP_PLUGIN_URL . 'assets/app.js',
			array(),
			LJLK_HOROSCOOP_VERSION,
			true
		);
		wp_enqueue_style(
			self::APP_STYLE,
			LJLK_HOROSCOOP_PLUGIN_URL . 'assets/app.css',
			array(),
			LJLK_HOROSCOOP_VERSION
		);
		wp_localize_script( self::APP_SCRIPT, 'ljlkHoroscoop', array(
			'restUrl'   => rest_url( LJLK_Horoscoop_REST::NAMESPACE . '/' ),
			'nonce'     => wp_create_nonce( 'wp_rest' ),
			'loggedIn'  => is_user_logged_in(),
			'apiBase'   => $base,
			'i18n'      => array(
				'compute'       => __( 'Berekenen', 'ljlk-horoscoop' ),
				'save'          => __( 'Opslaan', 'ljlk-horoscoop' ),
				'saved'         => __( 'Opgeslagen', 'ljlk-horoscoop' ),
				'birthDate'     => __( 'Geboortedatum', 'ljlk-horoscoop' ),
				'birthTime'     => __( 'Geboortetijd', 'ljlk-horoscoop' ),
				'advanced'      => __( 'Geavanceerd', 'ljlk-horoscoop' ),
				'latitude'      => __( 'Breedtegraad', 'ljlk-horoscoop' ),
				'longitude'     => __( 'Lengtegraad', 'ljlk-horoscoop' ),
				'timezone'      => __( 'Tijdzone (IANA)', 'ljlk-horoscoop' ),
				'utcOffset'     => __( 'UTC-offset (minuten)', 'ljlk-horoscoop' ),
				'western'       => __( 'Westers', 'ljlk-horoscoop' ),
				'sidereal'      => __( 'Siderisch', 'ljlk-horoscoop' ),
				'vedic'         => __( 'Vedisch', 'ljlk-horoscoop' ),
				'chinese'       => __( 'Chinees', 'ljlk-horoscoop' ),
				'diagnostics'   => __( 'Diagnostiek', 'ljlk-horoscoop' ),
				'rawJson'       => __( 'Ruwe JSON', 'ljlk-horoscoop' ),
				'register'      => __( 'Registreren', 'ljlk-horoscoop' ),
				'login'         => __( 'Inloggen', 'ljlk-horoscoop' ),
				'email'         => __( 'E-mail', 'ljlk-horoscoop' ),
				'password'      => __( 'Wachtwoord', 'ljlk-horoscoop' ),
				'minPassword'   => __( 'Min. 10 tekens', 'ljlk-horoscoop' ),
				'close'         => __( 'Sluiten', 'ljlk-horoscoop' ),
				'myHoroscopes'  => __( 'Mijn horoscopen', 'ljlk-horoscoop' ),
				'downloadJson'  => __( 'JSON downloaden', 'ljlk-horoscoop' ),
				'downloadSvg'   => __( 'Wiel (SVG)', 'ljlk-horoscoop' ),
				'downloadPdf'   => __( 'Rapport (PDF)', 'ljlk-horoscoop' ),
				'error'         => __( 'Fout', 'ljlk-horoscoop' ),
				'apiUnreachable'=> __( 'De horoscoop-service is niet bereikbaar. Probeer het later opnieuw.', 'ljlk-horoscoop' ),
				'story'         => __( 'Verhaal', 'ljlk-horoscoop' ),
				'storyHint'     => __( 'Gebruik de andere tabbladen voor de gestructureerde details; de ruwe JSON staat hieronder.', 'ljlk-horoscoop' ),
				'birthDateRequired' => __( 'Vul geboortedatum in.', 'ljlk-horoscoop' ),
				'computing'     => __( 'Bezig met berekenen…', 'ljlk-horoscoop' ),
				'emailRequired' => __( 'Vul e-mail in.', 'ljlk-horoscoop' ),
				'emailPasswordRequired' => __( 'Vul e-mail en wachtwoord in.', 'ljlk-horoscoop' ),
				'registerFailed' => __( 'Registratie mislukt', 'ljlk-horoscoop' ),
				'loginFailed'   => __( 'Inloggen mislukt', 'ljlk-horoscoop' ),
				'noSavedHoroscopes' => __( 'Geen opgeslagen horoscopen.', 'ljlk-horoscoop' ),
				'myHoroscope'   => __( 'Mijn horoscoop', 'ljlk-horoscoop' ),
				'birthDateLabel' => __( 'Geboortedatum:', 'ljlk-horoscoop' ),
				'dashboardLoadFailed' => __( 'Kon gegevens niet laden.', 'ljlk-horoscoop' ),
				'missingExactBirthTime' => __( 'exacte geboortetijd', 'ljlk-horoscoop' ),
				'missingBirthLocation' => __( 'geboortelocatie', 'ljlk-horoscoop' ),
				'missingTimezone' => __( 'tijdzone', 'ljlk-horoscoop' ),
				'missingGeneric' => __( 'één of meer invoervelden', 'ljlk-horoscoop' ),
				'inputCompletenessWarning' => __( 'Invoer is onvolledig of deels geschat ({missing}). Voor huizen en Ascendant zijn exacte tijd, locatie en tijdzone nodig; delen van de output kunnen daardoor ontbreken of minder precies zijn.', 'ljlk-horoscoop' ),
				'storyWhenProvided' => __( 'Op {when}', 'ljlk-horoscoop' ),
				'storyWhenFallback' => __( 'Op het moment dat je doorgaf', 'ljlk-horoscoop' ),
				'storyLocationPart' => __( ' op {where}', 'ljlk-horoscoop' ),
				'storyZonePart' => __( ' ({zone})', 'ljlk-horoscoop' ),
				'storyComputed' => __( '{when}{location}{zone} is je chart berekend.', 'ljlk-horoscoop' ),
				'storyHousePart' => __( ', huis {house}', 'ljlk-horoscoop' ),
				'storyWesternSun' => __( 'In het westerse verhaal staat je Zon in {sign}{house}.', 'ljlk-horoscoop' ),
				'storyWesternMoon' => __( 'Je Maan staat in {sign}{house}.', 'ljlk-horoscoop' ),
				'storyVedic' => __( 'In de vedische kalender leest de tijd als: {bits}.', 'ljlk-horoscoop' ),
				'storyVedicVaara' => __( 'Vaara: {value}', 'ljlk-horoscoop' ),
				'storyVedicTithi' => __( 'Tithi: {value}', 'ljlk-horoscoop' ),
				'storyVedicNakshatra' => __( 'Nakshatra: {value}', 'ljlk-horoscoop' ),
				'storyVedicYoga' => __( 'Yoga: {value}', 'ljlk-horoscoop' ),
				'storyBazi' => __( 'In BaZi laten de vier pilaren zien: {bits}.', 'ljlk-horoscoop' ),
				'storyBaziYear' => __( 'jaar {value}', 'ljlk-horoscoop' ),
				'storyBaziMonth' => __( 'maand {value}', 'ljlk-horoscoop' ),
				'storyBaziDay' => __( 'dag {value}', 'ljlk-horoscoop' ),
				'storyBaziHour' => __( 'uur {value}', 'ljlk-horoscoop' ),
				'rateLimit' => __( 'Snelheidslimiet bereikt', 'ljlk-horoscoop' ),
				'loginRequiredIndicator' => __( 'Log in', 'ljlk-horoscoop' ),
			),
		) );
	}

	public static function add_settings_page() {
		add_options_page(
			__( 'LJLK Horoscoop', 'ljlk-horoscoop' ),
			__( 'LJLK Horoscoop', 'ljlk-horoscoop' ),
			'manage_options',
			'ljlk-horoscoop',
			array( __CLASS__, 'render_settings_page' )
		);
	}

	public static function register_settings() {
		register_setting( 'ljlk_horoscoop', 'ljlk_horoscoop_api_base_url', array(
			'type'              => 'string',
			'sanitize_callback' => 'esc_url_raw',
		) );
		register_setting( 'ljlk_horoscoop', 'ljlk_horoscoop_cache_svg_pdf', array(
			'type'    => 'boolean',
			'default' => false,
		) );
		register_setting( 'ljlk_horoscoop', 'ljlk_horoscoop_max_saves_per_user', array(
			'type'    => 'integer',
			'default' => 10,
		) );
		register_setting( 'ljlk_horoscoop', 'ljlk_horoscoop_rate_limit_per_hour', array(
			'type'    => 'integer',
			'default' => 60,
		) );
	}

	public static function render_settings_page() {
		if ( ! current_user_can( 'manage_options' ) ) {
			return;
		}
		?>
		<div class="wrap">
			<h1><?php esc_html_e( 'LJLK Horoscoop-instellingen', 'ljlk-horoscoop' ); ?></h1>
			<form method="post" action="options.php">
				<?php settings_fields( 'ljlk_horoscoop' ); ?>
				<table class="form-table">
					<tr>
						<th><label for="ljlk_horoscoop_api_base_url"><?php esc_html_e( 'Python API Basis-URL', 'ljlk-horoscoop' ); ?></label></th>
						<td>
							<input type="url" id="ljlk_horoscoop_api_base_url" name="ljlk_horoscoop_api_base_url" value="<?php echo esc_attr( get_option( 'ljlk_horoscoop_api_base_url', '' ) ); ?>" class="regular-text" placeholder="https://api.example.com" />
							<p class="description"><?php esc_html_e( 'Verplicht. Basis-URL van de horoscoop-API (zonder afsluitende slash).', 'ljlk-horoscoop' ); ?></p>
						</td>
					</tr>
					<tr>
						<th><label for="ljlk_horoscoop_cache_svg_pdf"><?php esc_html_e( 'SVG/PDF cachen', 'ljlk-horoscoop' ); ?></label></th>
						<td>
							<input type="checkbox" id="ljlk_horoscoop_cache_svg_pdf" name="ljlk_horoscoop_cache_svg_pdf" value="1" <?php checked( get_option( 'ljlk_horoscoop_cache_svg_pdf', false ) ); ?> />
							<span><?php esc_html_e( 'Wiel (SVG) en rapport (PDF) bij opslaan ophalen en opslaan.', 'ljlk-horoscoop' ); ?></span>
						</td>
					</tr>
					<tr>
						<th><label for="ljlk_horoscoop_max_saves_per_user"><?php esc_html_e( 'Max. horoscopen per gebruiker', 'ljlk-horoscoop' ); ?></label></th>
						<td>
							<input type="number" id="ljlk_horoscoop_max_saves_per_user" name="ljlk_horoscoop_max_saves_per_user" value="<?php echo esc_attr( get_option( 'ljlk_horoscoop_max_saves_per_user', 10 ) ); ?>" min="1" max="100" />
						</td>
					</tr>
					<tr>
						<th><label for="ljlk_horoscoop_rate_limit_per_hour"><?php esc_html_e( 'Rate limit (berekeningen per uur per IP)', 'ljlk-horoscoop' ); ?></label></th>
						<td>
							<input type="number" id="ljlk_horoscoop_rate_limit_per_hour" name="ljlk_horoscoop_rate_limit_per_hour" value="<?php echo esc_attr( get_option( 'ljlk_horoscoop_rate_limit_per_hour', 60 ) ); ?>" min="0" />
							<p class="description"><?php esc_html_e( '0 = geen limiet.', 'ljlk-horoscoop' ); ?></p>
						</td>
					</tr>
				</table>
				<?php submit_button(); ?>
			</form>
		</div>
		<?php
	}

	/**
	 * Shortcode [ljlk_horoscoop_app]: compute form + save + register/login modal.
	 */
	public static function render_app() {
		ob_start();
		?>
		<div id="ljlk-horoscoop-app" class="ljlk-horoscoop-app">
			<div class="ljlk-horoscoop-form">
				<label for="ljlk-birth-date"><?php echo esc_html( __( 'Geboortedatum', 'ljlk-horoscoop' ) ); ?> <span class="required">*</span></label>
				<input type="date" id="ljlk-birth-date" name="birth_date" required />
				<div class="ljlk-advanced-toggle">
					<button type="button" class="ljlk-accordion-btn" aria-expanded="false"><?php echo esc_html( __( 'Geavanceerd', 'ljlk-horoscoop' ) ); ?></button>
					<div class="ljlk-advanced-fields" hidden>
						<label for="ljlk-birth-time"><?php echo esc_html( __( 'Geboortetijd', 'ljlk-horoscoop' ) ); ?></label>
						<input type="time" id="ljlk-birth-time" name="birth_time" step="1" />
						<label for="ljlk-latitude"><?php echo esc_html( __( 'Breedtegraad', 'ljlk-horoscoop' ) ); ?></label>
						<input type="number" id="ljlk-latitude" name="latitude" step="any" placeholder="52.0" />
						<label for="ljlk-longitude"><?php echo esc_html( __( 'Lengtegraad', 'ljlk-horoscoop' ) ); ?></label>
						<input type="number" id="ljlk-longitude" name="longitude" step="any" placeholder="5.0" />
						<label for="ljlk-timezone"><?php echo esc_html( __( 'Tijdzone (IANA)', 'ljlk-horoscoop' ) ); ?></label>
						<input type="text" id="ljlk-timezone" name="timezone_iana" placeholder="Europe/Amsterdam" />
						<label for="ljlk-utc-offset"><?php echo esc_html( __( 'UTC-offset (minuten)', 'ljlk-horoscoop' ) ); ?></label>
						<input type="number" id="ljlk-utc-offset" name="utc_offset_minutes" placeholder="60" />
					</div>
				</div>
				<div class="ljlk-actions">
					<button type="button" id="ljlk-compute-btn" class="ljlk-btn ljlk-btn-primary"><?php echo esc_html( __( 'Berekenen', 'ljlk-horoscoop' ) ); ?></button>
					<button type="button" id="ljlk-save-btn" class="ljlk-btn ljlk-btn-secondary"><?php echo esc_html( __( 'Opslaan', 'ljlk-horoscoop' ) ); ?></button>
				</div>
			</div>
			<div id="ljlk-result" class="ljlk-result" aria-live="polite"></div>
			<!-- Register / Login modal -->
			<div id="ljlk-auth-modal" class="ljlk-modal" role="dialog" aria-labelledby="ljlk-auth-title" aria-modal="true" hidden>
				<div class="ljlk-modal-content">
					<h2 id="ljlk-auth-title"><?php echo esc_html( __( 'Opslaan', 'ljlk-horoscoop' ) ); ?></h2>
					<p class="ljlk-auth-intro"><?php echo esc_html( __( 'Log in of maak een account aan (alleen e-mail en wachtwoord) om je horoscoop op te slaan.', 'ljlk-horoscoop' ) ); ?></p>
					<div id="ljlk-auth-tabs">
						<button type="button" class="ljlk-tab active" data-tab="login"><?php echo esc_html( __( 'Inloggen', 'ljlk-horoscoop' ) ); ?></button>
						<button type="button" class="ljlk-tab" data-tab="register"><?php echo esc_html( __( 'Registreren', 'ljlk-horoscoop' ) ); ?></button>
					</div>
					<div id="ljlk-login-form" class="ljlk-auth-form">
						<label for="ljlk-login-email"><?php echo esc_html( __( 'E-mail', 'ljlk-horoscoop' ) ); ?></label>
						<input type="email" id="ljlk-login-email" />
						<label for="ljlk-login-password"><?php echo esc_html( __( 'Wachtwoord', 'ljlk-horoscoop' ) ); ?></label>
						<input type="password" id="ljlk-login-password" />
						<button type="button" id="ljlk-do-login" class="ljlk-btn ljlk-btn-primary"><?php echo esc_html( __( 'Inloggen', 'ljlk-horoscoop' ) ); ?></button>
					</div>
					<div id="ljlk-register-form" class="ljlk-auth-form" hidden>
						<label for="ljlk-reg-email"><?php echo esc_html( __( 'E-mail', 'ljlk-horoscoop' ) ); ?></label>
						<input type="email" id="ljlk-reg-email" />
						<label for="ljlk-reg-password"><?php echo esc_html( __( 'Wachtwoord', 'ljlk-horoscoop' ) ); ?> <span class="ljlk-hint">(<?php echo esc_html( __( 'Min. 10 tekens', 'ljlk-horoscoop' ) ); ?>)</span></label>
						<input type="password" id="ljlk-reg-password" minlength="10" />
						<button type="button" id="ljlk-do-register" class="ljlk-btn ljlk-btn-primary"><?php echo esc_html( __( 'Registreren', 'ljlk-horoscoop' ) ); ?></button>
					</div>
					<div id="ljlk-auth-message" class="ljlk-auth-message" role="alert"></div>
					<button type="button" class="ljlk-modal-close" aria-label="<?php echo esc_attr( __( 'Sluiten', 'ljlk-horoscoop' ) ); ?>">&times;</button>
				</div>
			</div>
		</div>
		<?php
		return ob_get_clean();
	}

	/**
	 * Shortcode [ljlk_horoscoop_dashboard]: list saved horoscopes with download links.
	 */
	public static function render_dashboard() {
		if ( ! is_user_logged_in() ) {
			return '<p class="ljlk-dashboard-guest">' . esc_html__( 'Log in om je opgeslagen horoscopen te zien.', 'ljlk-horoscoop' ) . '</p>';
		}
		ob_start();
		?>
		<div id="ljlk-horoscoop-dashboard" class="ljlk-horoscoop-dashboard">
			<h2><?php echo esc_html( __( 'Mijn horoscopen', 'ljlk-horoscoop' ) ); ?></h2>
			<div id="ljlk-dashboard-list"></div>
		</div>
		<?php
		return ob_get_clean();
	}
}
