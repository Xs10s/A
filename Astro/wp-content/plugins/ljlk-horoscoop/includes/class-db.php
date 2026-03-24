<?php
/**
 * Database tables and migrations for horoscope profiles and runs.
 *
 * @package LJLK_Horoscoop
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class LJLK_Horoscoop_DB {

	const PROFILES_TABLE = 'ljlk_horoscope_profiles';
	const RUNS_TABLE     = 'ljlk_horoscope_runs';

	/**
	 * Run on plugin activation: create or update tables.
	 */
	public static function activate() {
		global $wpdb;
		$charset_collate = $wpdb->get_charset_collate();
		$prefix          = $wpdb->prefix;

		$profiles_sql = "CREATE TABLE {$prefix}" . self::PROFILES_TABLE . " (
			id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
			user_id bigint(20) unsigned NOT NULL,
			label varchar(100) DEFAULT 'Mijn horoscoop',
			birth_date date NOT NULL,
			birth_time time NULL,
			latitude double NULL,
			longitude double NULL,
			timezone_iana varchar(64) NULL,
			utc_offset_minutes smallint NULL,
			settings_json longtext NULL,
			created_at datetime NOT NULL,
			PRIMARY KEY (id),
			KEY user_id (user_id)
		) $charset_collate;";

		$runs_sql = "CREATE TABLE {$prefix}" . self::RUNS_TABLE . " (
			id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
			profile_id bigint(20) unsigned NOT NULL,
			input_hash char(64) NOT NULL,
			engine_version varchar(32) NULL,
			computed_at datetime NOT NULL,
			horoscoop_json longtext NOT NULL,
			wheel_svg longtext NULL,
			report_pdf longblob NULL,
			report_pdf_url text NULL,
			PRIMARY KEY (id),
			KEY profile_id (profile_id),
			KEY input_hash (input_hash),
			UNIQUE KEY profile_input (profile_id, input_hash)
		) $charset_collate;";

		require_once ABSPATH . 'wp-admin/includes/upgrade.php';
		dbDelta( $profiles_sql );
		dbDelta( $runs_sql );

		update_option( 'ljlk_horoscoop_db_version', '1.0' );
	}

	/**
	 * Get full table name for profiles.
	 *
	 * @return string
	 */
	public static function profiles_table() {
		global $wpdb;
		return $wpdb->prefix . self::PROFILES_TABLE;
	}

	/**
	 * Get full table name for runs.
	 *
	 * @return string
	 */
	public static function runs_table() {
		global $wpdb;
		return $wpdb->prefix . self::RUNS_TABLE;
	}
}
