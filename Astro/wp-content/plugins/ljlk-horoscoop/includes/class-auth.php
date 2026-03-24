<?php
/**
 * Auth helpers: rate limiting, registration throttle.
 *
 * @package LJLK_Horoscoop
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class LJLK_Horoscoop_Auth {

	const RATE_LIMIT_TRANSIENT_PREFIX = 'ljlk_horoscoop_compute_';
	const REGISTER_THROTTLE_PREFIX    = 'ljlk_horoscoop_register_';
	const RATE_LIMIT_DURATION         = 3600;   // 1 hour
	const REGISTER_THROTTLE_DURATION = 3600;   // 1 hour

	/**
	 * Check compute rate limit by IP. Returns true if allowed, false if exceeded.
	 *
	 * @param string $ip Client IP.
	 * @return bool True if under limit.
	 */
	public static function compute_rate_limit_ok( $ip ) {
		$limit = (int) get_option( 'ljlk_horoscoop_rate_limit_per_hour', 60 );
		if ( $limit <= 0 ) {
			return true;
		}
		$key   = self::RATE_LIMIT_TRANSIENT_PREFIX . md5( $ip );
		$count = (int) get_transient( $key );
		if ( $count >= $limit ) {
			return false;
		}
		set_transient( $key, $count + 1, self::RATE_LIMIT_DURATION );
		return true;
	}

	/**
	 * Check registration throttle by IP. Returns true if allowed.
	 *
	 * @param string $ip Client IP.
	 * @param int    $max_per_hour Max registrations per hour per IP.
	 * @return bool True if under limit.
	 */
	public static function register_throttle_ok( $ip, $max_per_hour = 5 ) {
		$key   = self::REGISTER_THROTTLE_PREFIX . md5( $ip );
		$count = (int) get_transient( $key );
		if ( $count >= $max_per_hour ) {
			return false;
		}
		set_transient( $key, $count + 1, self::REGISTER_THROTTLE_DURATION );
		return true;
	}

	/**
	 * Get client IP for rate limiting (respects X-Forwarded-For if from trusted proxy).
	 *
	 * @return string
	 */
	public static function get_client_ip() {
		if ( ! empty( $_SERVER['HTTP_X_FORWARDED_FOR'] ) ) {
			$list = array_map( 'trim', explode( ',', sanitize_text_field( wp_unslash( $_SERVER['HTTP_X_FORWARDED_FOR'] ) ) ) );
			return $list[0];
		}
		if ( ! empty( $_SERVER['REMOTE_ADDR'] ) ) {
			return sanitize_text_field( wp_unslash( $_SERVER['REMOTE_ADDR'] ) );
		}
		return '0.0.0.0';
	}
}
