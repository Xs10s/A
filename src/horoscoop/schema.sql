-- Astrologische reken- en kennisbank: volledige schema
-- Bron: Specificatie voor een astrologische reken- en kennisbank
-- IERS TN36, SE API, VedicDateTime, YT Liu (Chinese)

-- =============================================================================
-- ITEM TYPEN EN ITEMS (woordenboeklaag)
-- =============================================================================

CREATE TABLE kb_item_type (
    type_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code          TEXT NOT NULL UNIQUE,
    description   TEXT,
    CONSTRAINT chk_item_type_code CHECK (code IN (
        'body', 'sign', 'house', 'aspect', 'ayanamsha', 'house_system',
        'solar_term', 'stem', 'branch', 'nakshatra', 'tithi', 'yoga', 'karana'
    ))
);
COMMENT ON TABLE kb_item_type IS 'Typologie van items; code enum: body/sign/house/aspect/ayanamsha/house_system/solar_term/stem/branch/nakshatra/tithi/yoga/karana';

CREATE TABLE kb_item (
    item_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_id    UUID NOT NULL REFERENCES kb_item_type(type_id),
    code       TEXT NOT NULL,
    name_nl    TEXT,
    name_en    TEXT,
    is_active  BOOLEAN NOT NULL DEFAULT true,
    sort_order INT,
    UNIQUE (type_id, code)
);
COMMENT ON COLUMN kb_item.code IS 'Stable key for programmatic use';
COMMENT ON COLUMN kb_item.sort_order IS 'Display order';

CREATE TABLE kb_item_alias (
    alias_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_id    UUID NOT NULL REFERENCES kb_item(item_id),
    alias      TEXT NOT NULL,
    locale     TEXT,
    script     TEXT,
    confidence NUMERIC(3,2) CHECK (confidence >= 0 AND confidence <= 1),
    CONSTRAINT chk_script CHECK (script IN ('latn', 'deva', 'hani'))
);
COMMENT ON COLUMN kb_item_alias.script IS 'enum: latn/deva/hani';

CREATE TABLE kb_tag (
    tag_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code         TEXT NOT NULL UNIQUE,
    label_nl     TEXT,
    parent_tag_id UUID REFERENCES kb_tag(tag_id)
);

CREATE TABLE kb_item_tag (
    item_id UUID NOT NULL REFERENCES kb_item(item_id),
    tag_id  UUID NOT NULL REFERENCES kb_tag(tag_id),
    weight  DOUBLE PRECISION,
    PRIMARY KEY (item_id, tag_id)
);

-- =============================================================================
-- PROPERTIES (waardes/eigenschappen)
-- =============================================================================

CREATE TABLE kb_property_def (
    prop_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code        TEXT NOT NULL UNIQUE,
    value_type  TEXT NOT NULL,
    unit        TEXT,
    domain      TEXT,
    description TEXT,
    CONSTRAINT chk_value_type CHECK (value_type IN ('float', 'int', 'text', 'bool', 'json'))
);
COMMENT ON COLUMN kb_property_def.unit IS 'e.g. deg, rad, s, au';
COMMENT ON COLUMN kb_property_def.domain IS 'e.g. astronomy/astrology/interpretation';

CREATE TABLE kb_property_enum (
    enum_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prop_id   UUID NOT NULL REFERENCES kb_property_def(prop_id),
    enum_code TEXT NOT NULL,
    label_nl  TEXT,
    UNIQUE (prop_id, enum_code)
);

CREATE TABLE kb_item_property (
    item_id      UUID NOT NULL REFERENCES kb_item(item_id),
    prop_id      UUID NOT NULL REFERENCES kb_property_def(prop_id),
    value_float  DOUBLE PRECISION,
    value_int    BIGINT,
    value_text   TEXT,
    value_bool   BOOLEAN,
    value_json   JSONB,
    source_id    UUID,
    valid_from   TIMESTAMPTZ,
    valid_to     TIMESTAMPTZ,
    PRIMARY KEY (item_id, prop_id),
    CONSTRAINT chk_one_value CHECK (
        (value_float IS NOT NULL)::int + (value_int IS NOT NULL)::int +
        (value_text IS NOT NULL)::int + (value_bool IS NOT NULL)::int +
        (value_json IS NOT NULL)::int = 1
    )
);

-- =============================================================================
-- INTERPRETATIES (snippets + triggers)
-- =============================================================================

CREATE TABLE kb_interp_snippet (
    snippet_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title_nl      TEXT,
    text_nl       TEXT NOT NULL,
    tone          TEXT,
    evidence_style TEXT,
    min_length    INT,
    max_length    INT,
    CONSTRAINT chk_tone CHECK (tone IN ('neutraal', 'coachend', 'technisch')),
    CONSTRAINT chk_evidence_style CHECK (evidence_style IN ('modern', 'traditional', 'synthesis'))
);

CREATE TABLE kb_interp_trigger (
    trigger_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snippet_id     UUID NOT NULL REFERENCES kb_interp_snippet(snippet_id),
    trigger_json   JSONB NOT NULL,
    priority       INT NOT NULL,
    confidence_hint NUMERIC(3,2) CHECK (confidence_hint >= 0 AND confidence_hint <= 1)
);
COMMENT ON COLUMN kb_interp_trigger.trigger_json IS 'DSL (e.g. JSONLogic): placements, aspects, element_balance, patterns';

CREATE TABLE kb_interp_snippet_tag (
    snippet_id UUID NOT NULL REFERENCES kb_interp_snippet(snippet_id),
    tag_id     UUID NOT NULL REFERENCES kb_tag(tag_id),
    weight     DOUBLE PRECISION,
    PRIMARY KEY (snippet_id, tag_id)
);

CREATE TABLE kb_interp_template (
    template_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code           TEXT NOT NULL UNIQUE,
    render_order   INT NOT NULL,
    template_text_nl TEXT NOT NULL
);

-- =============================================================================
-- WEIGHTS, RULES, SCORING, FEATURES
-- =============================================================================

CREATE TABLE kb_scoring_profile (
    profile_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code        TEXT NOT NULL UNIQUE,
    description TEXT,
    is_default  BOOLEAN NOT NULL DEFAULT false
);

CREATE TABLE kb_weight_rule (
    rule_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL REFERENCES kb_scoring_profile(profile_id),
    target     TEXT NOT NULL,
    rule_json  JSONB NOT NULL,
    weight     DOUBLE PRECISION NOT NULL,
    notes      TEXT,
    CONSTRAINT chk_target CHECK (target IN ('aspect', 'placement', 'house', 'planet'))
);

CREATE TABLE kb_feature_def (
    feature_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code           TEXT NOT NULL UNIQUE,
    output_schema  JSONB,
    description    TEXT
);

CREATE TABLE kb_feature_rule (
    rule_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    feature_id UUID NOT NULL REFERENCES kb_feature_def(feature_id),
    rule_json JSONB NOT NULL
);
COMMENT ON COLUMN kb_feature_rule.rule_json IS 'Parameters: orb, sets, exceptions for detection';

-- =============================================================================
-- BRONNEN, FORMULES, MODELVERSIES, AUDIT
-- =============================================================================

CREATE TABLE kb_source (
    source_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title       TEXT NOT NULL,
    publisher   TEXT,
    year        INT,
    version     TEXT,
    url_or_ref  TEXT,
    license     TEXT
);

CREATE TABLE kb_formula_def (
    formula_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code             TEXT NOT NULL UNIQUE,
    latex            TEXT,
    algorithm_steps  TEXT,
    source_id        UUID REFERENCES kb_source(source_id)
);

CREATE TABLE kb_model_version (
    model_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code           TEXT NOT NULL,
    version_string TEXT NOT NULL,
    notes          TEXT,
    source_id      UUID REFERENCES kb_source(source_id)
);

CREATE TABLE calc_run_log (
    run_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    input_json       JSONB NOT NULL,
    settings_json    JSONB,
    engine_versions  JSONB NOT NULL,
    created_at_utc   TIMESTAMPTZ NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    result_hash      TEXT
);
COMMENT ON TABLE calc_run_log IS 'Audit trail: input, settings, engine versions, result hash for reproducibility';

-- =============================================================================
-- INDEXES
-- =============================================================================

CREATE INDEX idx_kb_item_type_code ON kb_item_type(code);
CREATE INDEX idx_kb_item_type_code_code ON kb_item(type_id, code);
CREATE INDEX idx_kb_item_tag_tag ON kb_item_tag(tag_id);
CREATE INDEX idx_kb_item_property_prop ON kb_item_property(prop_id);
CREATE INDEX idx_kb_interp_trigger_snippet ON kb_interp_trigger(snippet_id);
CREATE INDEX idx_calc_run_log_created ON calc_run_log(created_at_utc);
