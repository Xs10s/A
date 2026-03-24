<?php
/**
 * Canonical hashing and sanitization helpers.
 *
 * @package LJLK_Horoscoop
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Canonicalize payload for hashing: sort keys, normalize missing optionals to null.
 *
 * @param array $payload Raw request payload (birth_date, birth_time, lat, lon, etc.).
 * @return string JSON string with sorted keys.
 */
function ljlk_horoscoop_canonical_json( array $payload ) {
	$keys = array(
		'birth_date',
		'birth_time',
		'birth_time_local',
		'latitude',
		'longitude',
		'lat',
		'lon',
		'timezone_iana',
		'utc_offset_minutes',
		'utc_offset_hours',
		'settings',
	);
	$normalized = array();
	foreach ( $keys as $k ) {
		if ( array_key_exists( $k, $payload ) ) {
			$normalized[ $k ] = $payload[ $k ];
		} else {
			$normalized[ $k ] = null;
		}
	}
	if ( isset( $normalized['settings'] ) && is_array( $normalized['settings'] ) ) {
		ksort( $normalized['settings'] );
	}
	ksort( $normalized );
	return wp_json_encode( $normalized, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE );
}

/**
 * Compute input hash for deduplication (profile_id + input_hash unique).
 *
 * @param array $payload Same shape as canonical_json.
 * @return string 64-char hex SHA256.
 */
function ljlk_horoscoop_input_hash( array $payload ) {
	return hash( 'sha256', ljlk_horoscoop_canonical_json( $payload ) );
}

/**
 * Validate birth_date as YYYY-MM-DD.
 *
 * @param string $date Date string.
 * @return bool True if valid.
 */
function ljlk_horoscoop_validate_birth_date( $date ) {
	if ( ! is_string( $date ) || strlen( $date ) < 10 ) {
		return false;
	}
	$d = DateTime::createFromFormat( 'Y-m-d', substr( $date, 0, 10 ) );
	return $d && $d->format( 'Y-m-d' ) === substr( $date, 0, 10 );
}

/**
 * Validate optional time as HH:MM or HH:MM:SS.
 *
 * @param string|null $time Time string.
 * @return bool True if empty or valid.
 */
function ljlk_horoscoop_validate_birth_time( $time ) {
	if ( $time === null || $time === '' ) {
		return true;
	}
	return (bool) preg_match( '/^\d{1,2}:\d{2}(:\d{2})?$/', trim( (string) $time ) );
}

/**
 * Sanitize payload for Python API: map frontend keys to API keys.
 *
 * @param array $input From REST request.
 * @return array Payload for POST /api/horoscoop.
 */
function ljlk_horoscoop_sanitize_for_api( array $input ) {
	$out = array(
		'birth_date' => isset( $input['birth_date'] ) ? sanitize_text_field( $input['birth_date'] ) : null,
		'birth_time_local' => null,
		'lat' => null,
		'lon' => null,
		'timezone_iana' => isset( $input['timezone_iana'] ) ? sanitize_text_field( $input['timezone_iana'] ) : null,
		'utc_offset_minutes' => isset( $input['utc_offset_minutes'] ) ? ljlk_horoscoop_sanitize_int( $input['utc_offset_minutes'], -720, 720 ) : null,
	);
	if ( ! empty( $input['birth_time'] ) ) {
		$out['birth_time_local'] = sanitize_text_field( $input['birth_time'] );
	} elseif ( ! empty( $input['birth_time_local'] ) ) {
		$out['birth_time_local'] = sanitize_text_field( $input['birth_time_local'] );
	}
	if ( isset( $input['latitude'] ) && $input['latitude'] !== '' && $input['latitude'] !== null ) {
		$out['lat'] = floatval( $input['latitude'] );
	} elseif ( isset( $input['lat'] ) && $input['lat'] !== '' && $input['lat'] !== null ) {
		$out['lat'] = floatval( $input['lat'] );
	}
	if ( isset( $input['longitude'] ) && $input['longitude'] !== '' && $input['longitude'] !== null ) {
		$out['lon'] = floatval( $input['longitude'] );
	} elseif ( isset( $input['lon'] ) && $input['lon'] !== '' && $input['lon'] !== null ) {
		$out['lon'] = floatval( $input['lon'] );
	}
	if ( ! empty( $input['settings'] ) && is_array( $input['settings'] ) ) {
		$out['settings'] = $input['settings'];
	}
	return $out;
}

/**
 * Sanitize integer within range.
 *
 * @param mixed $v Value.
 * @param int   $min Min.
 * @param int   $max Max.
 * @return int|null
 */
function ljlk_horoscoop_sanitize_int( $v, $min, $max ) {
	$n = intval( $v );
	if ( $n < $min || $n > $max ) {
		return null;
	}
	return $n;
}
