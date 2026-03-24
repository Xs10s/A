<?php
/**
 * Plugin Name: LJLK Horoscoop
 * Description: Compute-first astrology feature for Elementor. Anonymous compute; save on demand with email+password registration.
 * Version: 1.0.0
 * Author: LJLK
 * Text Domain: ljlk-horoscoop
 * Requires at least: 5.8
 * Requires PHP: 7.4
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'LJLK_HOROSCOOP_VERSION', '1.0.0' );
define( 'LJLK_HOROSCOOP_PLUGIN_DIR', plugin_dir_path( __FILE__ ) );
define( 'LJLK_HOROSCOOP_PLUGIN_URL', plugin_dir_url( __FILE__ ) );

require_once LJLK_HOROSCOOP_PLUGIN_DIR . 'includes/helpers.php';
require_once LJLK_HOROSCOOP_PLUGIN_DIR . 'includes/class-db.php';
require_once LJLK_HOROSCOOP_PLUGIN_DIR . 'includes/class-client.php';
require_once LJLK_HOROSCOOP_PLUGIN_DIR . 'includes/class-auth.php';
require_once LJLK_HOROSCOOP_PLUGIN_DIR . 'includes/class-rest.php';
require_once LJLK_HOROSCOOP_PLUGIN_DIR . 'includes/class-shortcodes.php';

register_activation_hook( __FILE__, array( 'LJLK_Horoscoop_DB', 'activate' ) );

add_action( 'init', array( 'LJLK_Horoscoop_REST', 'register_routes' ) );
add_action( 'rest_api_init', array( 'LJLK_Horoscoop_REST', 'register_routes' ) );
add_filter( 'rest_pre_serve_request', array( 'LJLK_Horoscoop_REST', 'serve_raw_download' ), 10, 4 );
add_action( 'wp_enqueue_scripts', array( 'LJLK_Horoscoop_Shortcodes', 'enqueue_assets' ) );
add_action( 'admin_menu', array( 'LJLK_Horoscoop_Shortcodes', 'add_settings_page' ) );
add_action( 'admin_init', array( 'LJLK_Horoscoop_Shortcodes', 'register_settings' ) );

add_shortcode( 'ljlk_horoscoop_app', array( 'LJLK_Horoscoop_Shortcodes', 'render_app' ) );
add_shortcode( 'ljlk_horoscoop_dashboard', array( 'LJLK_Horoscoop_Shortcodes', 'render_dashboard' ) );
