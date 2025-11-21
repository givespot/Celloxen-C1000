--
-- PostgreSQL database dump
--

\restrict OVe0vKovjhhZfiW7ThAd4Lxtu6JgMMpg1TAfvvVjGV37uyQZkZRORq4hfiuRG7R

-- Dumped from database version 16.10 (Ubuntu 16.10-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.10 (Ubuntu 16.10-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: appointmentstatus; Type: TYPE; Schema: public; Owner: celloxen_user
--

CREATE TYPE public.appointmentstatus AS ENUM (
    'SCHEDULED',
    'CONFIRMED',
    'CHECKED_IN',
    'IN_PROGRESS',
    'COMPLETED',
    'CANCELLED',
    'NO_SHOW',
    'RESCHEDULED'
);


ALTER TYPE public.appointmentstatus OWNER TO celloxen_user;

--
-- Name: appointmenttype; Type: TYPE; Schema: public; Owner: celloxen_user
--

CREATE TYPE public.appointmenttype AS ENUM (
    'INITIAL_ASSESSMENT',
    'FOLLOW_UP',
    'THERAPY_SESSION',
    'REVIEW',
    'CONSULTATION'
);


ALTER TYPE public.appointmenttype OWNER TO celloxen_user;

--
-- Name: assessmentstatus; Type: TYPE; Schema: public; Owner: celloxen_user
--

CREATE TYPE public.assessmentstatus AS ENUM (
    'IN_PROGRESS',
    'COMPLETED',
    'ABANDONED'
);


ALTER TYPE public.assessmentstatus OWNER TO celloxen_user;

--
-- Name: assessmenttype; Type: TYPE; Schema: public; Owner: celloxen_user
--

CREATE TYPE public.assessmenttype AS ENUM (
    'INITIAL',
    'MID_COURSE',
    'FINAL',
    'FOLLOW_UP'
);


ALTER TYPE public.assessmenttype OWNER TO celloxen_user;

--
-- Name: clinicstatus; Type: TYPE; Schema: public; Owner: celloxen_user
--

CREATE TYPE public.clinicstatus AS ENUM (
    'ACTIVE',
    'INACTIVE',
    'SUSPENDED'
);


ALTER TYPE public.clinicstatus OWNER TO celloxen_user;

--
-- Name: gender; Type: TYPE; Schema: public; Owner: celloxen_user
--

CREATE TYPE public.gender AS ENUM (
    'MALE',
    'FEMALE',
    'OTHER',
    'PREFER_NOT_TO_SAY'
);


ALTER TYPE public.gender OWNER TO celloxen_user;

--
-- Name: notificationchannel; Type: TYPE; Schema: public; Owner: celloxen_user
--

CREATE TYPE public.notificationchannel AS ENUM (
    'EMAIL',
    'SMS',
    'IN_APP',
    'PUSH'
);


ALTER TYPE public.notificationchannel OWNER TO celloxen_user;

--
-- Name: notificationstatus; Type: TYPE; Schema: public; Owner: celloxen_user
--

CREATE TYPE public.notificationstatus AS ENUM (
    'PENDING',
    'SENT',
    'DELIVERED',
    'FAILED',
    'BOUNCED'
);


ALTER TYPE public.notificationstatus OWNER TO celloxen_user;

--
-- Name: patientstatus; Type: TYPE; Schema: public; Owner: celloxen_user
--

CREATE TYPE public.patientstatus AS ENUM (
    'ACTIVE',
    'INACTIVE',
    'ON_HOLD'
);


ALTER TYPE public.patientstatus OWNER TO celloxen_user;

--
-- Name: paymentstatus; Type: TYPE; Schema: public; Owner: celloxen_user
--

CREATE TYPE public.paymentstatus AS ENUM (
    'PENDING',
    'PAID',
    'WAIVED'
);


ALTER TYPE public.paymentstatus OWNER TO celloxen_user;

--
-- Name: questiontype; Type: TYPE; Schema: public; Owner: celloxen_user
--

CREATE TYPE public.questiontype AS ENUM (
    'SCALE_1_5',
    'YES_NO',
    'MULTIPLE_CHOICE',
    'SEVERITY_1_10'
);


ALTER TYPE public.questiontype OWNER TO celloxen_user;

--
-- Name: recipienttype; Type: TYPE; Schema: public; Owner: celloxen_user
--

CREATE TYPE public.recipienttype AS ENUM (
    'PATIENT',
    'CLINIC_STAFF',
    'SUPER_ADMIN'
);


ALTER TYPE public.recipienttype OWNER TO celloxen_user;

--
-- Name: subscriptionstatus; Type: TYPE; Schema: public; Owner: celloxen_user
--

CREATE TYPE public.subscriptionstatus AS ENUM (
    'TRIAL',
    'ACTIVE',
    'EXPIRED',
    'CANCELLED'
);


ALTER TYPE public.subscriptionstatus OWNER TO celloxen_user;

--
-- Name: therapydomain; Type: TYPE; Schema: public; Owner: celloxen_user
--

CREATE TYPE public.therapydomain AS ENUM (
    'DIABETICS',
    'CHRONIC_PAIN',
    'ANXIETY_STRESS',
    'ENERGY_VITALITY'
);


ALTER TYPE public.therapydomain OWNER TO celloxen_user;

--
-- Name: therapyplanstatus; Type: TYPE; Schema: public; Owner: celloxen_user
--

CREATE TYPE public.therapyplanstatus AS ENUM (
    'PENDING_APPROVAL',
    'APPROVED',
    'IN_PROGRESS',
    'COMPLETED',
    'CANCELLED'
);


ALTER TYPE public.therapyplanstatus OWNER TO celloxen_user;

--
-- Name: therapypriority; Type: TYPE; Schema: public; Owner: celloxen_user
--

CREATE TYPE public.therapypriority AS ENUM (
    'PRIMARY',
    'SECONDARY',
    'SUPPLEMENTARY'
);


ALTER TYPE public.therapypriority OWNER TO celloxen_user;

--
-- Name: therapysessionstatus; Type: TYPE; Schema: public; Owner: celloxen_user
--

CREATE TYPE public.therapysessionstatus AS ENUM (
    'SCHEDULED',
    'CHECKED_IN',
    'IN_PROGRESS',
    'COMPLETED',
    'CANCELLED',
    'NO_SHOW'
);


ALTER TYPE public.therapysessionstatus OWNER TO celloxen_user;

--
-- Name: userrole; Type: TYPE; Schema: public; Owner: celloxen_user
--

CREATE TYPE public.userrole AS ENUM (
    'SUPER_ADMIN',
    'CLINIC_USER',
    'PATIENT'
);


ALTER TYPE public.userrole OWNER TO celloxen_user;

--
-- Name: userstatus; Type: TYPE; Schema: public; Owner: celloxen_user
--

CREATE TYPE public.userstatus AS ENUM (
    'ACTIVE',
    'INACTIVE',
    'SUSPENDED'
);


ALTER TYPE public.userstatus OWNER TO celloxen_user;

--
-- Name: cleanup_abandoned_sessions(); Type: FUNCTION; Schema: public; Owner: celloxen_user
--

CREATE FUNCTION public.cleanup_abandoned_sessions() RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    UPDATE chatbot_sessions
    SET status = 'abandoned'
    WHERE status = 'active'
      AND last_activity_at < (CURRENT_TIMESTAMP - INTERVAL '24 hours');
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$;


ALTER FUNCTION public.cleanup_abandoned_sessions() OWNER TO celloxen_user;

--
-- Name: update_chatbot_updated_at(); Type: FUNCTION; Schema: public; Owner: celloxen_user
--

CREATE FUNCTION public.update_chatbot_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_chatbot_updated_at() OWNER TO celloxen_user;

--
-- Name: update_session_activity(); Type: FUNCTION; Schema: public; Owner: celloxen_user
--

CREATE FUNCTION public.update_session_activity() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE chatbot_sessions
    SET last_activity_at = CURRENT_TIMESTAMP
    WHERE id = NEW.session_id;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_session_activity() OWNER TO celloxen_user;

--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: celloxen_user
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO celloxen_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: appointments; Type: TABLE; Schema: public; Owner: celloxen_user
--

CREATE TABLE public.appointments (
    id bigint NOT NULL,
    appointment_number character varying(50) NOT NULL,
    clinic_id bigint NOT NULL,
    patient_id bigint NOT NULL,
    appointment_type public.appointmenttype NOT NULL,
    appointment_date date NOT NULL,
    appointment_time time without time zone NOT NULL,
    duration_minutes integer,
    practitioner_id bigint,
    therapist_id bigint,
    status public.appointmentstatus,
    booking_notes text,
    cancellation_reason text,
    cancelled_at timestamp with time zone,
    cancelled_by bigint,
    reminder_sent_24h boolean,
    reminder_sent_2h boolean,
    confirmation_sent boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    created_by bigint
);


ALTER TABLE public.appointments OWNER TO celloxen_user;

--
-- Name: appointments_id_seq; Type: SEQUENCE; Schema: public; Owner: celloxen_user
--

CREATE SEQUENCE public.appointments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.appointments_id_seq OWNER TO celloxen_user;

--
-- Name: appointments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: celloxen_user
--

ALTER SEQUENCE public.appointments_id_seq OWNED BY public.appointments.id;


--
-- Name: assessment_answers; Type: TABLE; Schema: public; Owner: celloxen_user
--

CREATE TABLE public.assessment_answers (
    id bigint NOT NULL,
    assessment_id bigint NOT NULL,
    question_id bigint NOT NULL,
    answer_value character varying(255) NOT NULL,
    answer_text text,
    score_contribution numeric(5,2),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.assessment_answers OWNER TO celloxen_user;

--
-- Name: assessment_answers_id_seq; Type: SEQUENCE; Schema: public; Owner: celloxen_user
--

CREATE SEQUENCE public.assessment_answers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.assessment_answers_id_seq OWNER TO celloxen_user;

--
-- Name: assessment_answers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: celloxen_user
--

ALTER SEQUENCE public.assessment_answers_id_seq OWNED BY public.assessment_answers.id;


--
-- Name: assessment_questions; Type: TABLE; Schema: public; Owner: celloxen_user
--

CREATE TABLE public.assessment_questions (
    id bigint NOT NULL,
    therapy_domain character varying(50) NOT NULL,
    question_text text NOT NULL,
    question_type character varying(20) DEFAULT 'multiple_choice'::character varying,
    question_order integer NOT NULL,
    response_options jsonb,
    scoring_weight numeric(3,2) DEFAULT 1.00,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.assessment_questions OWNER TO celloxen_user;

--
-- Name: TABLE assessment_questions; Type: COMMENT; Schema: public; Owner: celloxen_user
--

COMMENT ON TABLE public.assessment_questions IS 'Dynamic question bank for all therapy domain assessments';


--
-- Name: assessment_questions_id_seq; Type: SEQUENCE; Schema: public; Owner: celloxen_user
--

CREATE SEQUENCE public.assessment_questions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.assessment_questions_id_seq OWNER TO celloxen_user;

--
-- Name: assessment_questions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: celloxen_user
--

ALTER SEQUENCE public.assessment_questions_id_seq OWNED BY public.assessment_questions.id;


--
-- Name: assessments; Type: TABLE; Schema: public; Owner: celloxen_user
--

CREATE TABLE public.assessments (
    id bigint NOT NULL,
    assessment_number character varying(50) NOT NULL,
    clinic_id bigint NOT NULL,
    patient_id bigint NOT NULL,
    assessment_type public.assessmenttype,
    status public.assessmentstatus,
    questionnaire_started_at timestamp with time zone,
    questionnaire_completed_at timestamp with time zone,
    total_questions integer,
    questions_answered integer,
    iridology_included boolean,
    iridology_left_image character varying(255),
    iridology_right_image character varying(255),
    iridology_analysis_result text,
    diabetics_score numeric(5,2),
    chronic_pain_score numeric(5,2),
    anxiety_stress_score numeric(5,2),
    energy_vitality_score numeric(5,2),
    overall_wellness_score numeric(5,2),
    report_generated boolean,
    report_pdf_path character varying(255),
    report_generated_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    created_by bigint
);


ALTER TABLE public.assessments OWNER TO celloxen_user;

--
-- Name: assessments_id_seq; Type: SEQUENCE; Schema: public; Owner: celloxen_user
--

CREATE SEQUENCE public.assessments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.assessments_id_seq OWNER TO celloxen_user;

--
-- Name: assessments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: celloxen_user
--

ALTER SEQUENCE public.assessments_id_seq OWNED BY public.assessments.id;


--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: celloxen_user
--

CREATE TABLE public.audit_logs (
    id bigint NOT NULL,
    user_id bigint,
    user_email character varying(255),
    user_role character varying(50),
    clinic_id bigint,
    action character varying(100) NOT NULL,
    entity_type character varying(50) NOT NULL,
    entity_id bigint,
    old_values json,
    new_values json,
    changed_fields json,
    ip_address character varying(45),
    user_agent text,
    request_path character varying(500),
    request_method character varying(10),
    description text,
    audit_metadata json,
    success boolean,
    error_message text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.audit_logs OWNER TO celloxen_user;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: celloxen_user
--

CREATE SEQUENCE public.audit_logs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.audit_logs_id_seq OWNER TO celloxen_user;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: celloxen_user
--

ALTER SEQUENCE public.audit_logs_id_seq OWNED BY public.audit_logs.id;


--
-- Name: chatbot_messages; Type: TABLE; Schema: public; Owner: celloxen_user
--

CREATE TABLE public.chatbot_messages (
    id bigint NOT NULL,
    session_id bigint NOT NULL,
    sender_type character varying(20) NOT NULL,
    sender_id bigint,
    message_type character varying(50) NOT NULL,
    message_text text NOT NULL,
    question_id character varying(100),
    answer_value character varying(500),
    answer_score integer,
    metadata jsonb,
    read_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.chatbot_messages OWNER TO celloxen_user;

--
-- Name: chatbot_messages_id_seq; Type: SEQUENCE; Schema: public; Owner: celloxen_user
--

CREATE SEQUENCE public.chatbot_messages_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.chatbot_messages_id_seq OWNER TO celloxen_user;

--
-- Name: chatbot_messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: celloxen_user
--

ALTER SEQUENCE public.chatbot_messages_id_seq OWNED BY public.chatbot_messages.id;


--
-- Name: chatbot_questions_progress; Type: TABLE; Schema: public; Owner: celloxen_user
--

CREATE TABLE public.chatbot_questions_progress (
    id bigint NOT NULL,
    session_id bigint NOT NULL,
    domain character varying(50) NOT NULL,
    question_key character varying(100) NOT NULL,
    question_text text NOT NULL,
    response_value character varying(500),
    response_score integer,
    asked_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    answered_at timestamp without time zone,
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.chatbot_questions_progress OWNER TO celloxen_user;

--
-- Name: chatbot_questions_progress_id_seq; Type: SEQUENCE; Schema: public; Owner: celloxen_user
--

CREATE SEQUENCE public.chatbot_questions_progress_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.chatbot_questions_progress_id_seq OWNER TO celloxen_user;

--
-- Name: chatbot_questions_progress_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: celloxen_user
--

ALTER SEQUENCE public.chatbot_questions_progress_id_seq OWNED BY public.chatbot_questions_progress.id;


--
-- Name: chatbot_sessions; Type: TABLE; Schema: public; Owner: celloxen_user
--

CREATE TABLE public.chatbot_sessions (
    id bigint NOT NULL,
    session_token character varying(100) NOT NULL,
    session_type character varying(50) DEFAULT 'in_clinic_assessment'::character varying,
    patient_id bigint NOT NULL,
    practitioner_id bigint,
    clinic_id bigint,
    status character varying(20) DEFAULT 'active'::character varying,
    current_stage character varying(50) DEFAULT 'introduction'::character varying,
    questionnaire_reviewed boolean DEFAULT false,
    follow_up_questions_completed boolean DEFAULT false,
    left_eye_captured boolean DEFAULT false,
    right_eye_captured boolean DEFAULT false,
    ai_analysis_completed boolean DEFAULT false,
    assessment_id bigint,
    session_data jsonb DEFAULT '{}'::jsonb,
    started_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    completed_at timestamp without time zone,
    last_activity_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    duration_minutes integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.chatbot_sessions OWNER TO celloxen_user;

--
-- Name: chatbot_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: celloxen_user
--

CREATE SEQUENCE public.chatbot_sessions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.chatbot_sessions_id_seq OWNER TO celloxen_user;

--
-- Name: chatbot_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: celloxen_user
--

ALTER SEQUENCE public.chatbot_sessions_id_seq OWNED BY public.chatbot_sessions.id;


--
-- Name: clinics; Type: TABLE; Schema: public; Owner: celloxen_user
--

CREATE TABLE public.clinics (
    id bigint NOT NULL,
    name character varying(255) NOT NULL,
    email character varying(255) NOT NULL,
    phone character varying(50) NOT NULL,
    address_line1 character varying(255) NOT NULL,
    city character varying(100) NOT NULL,
    postcode character varying(20) NOT NULL,
    country character varying(100) DEFAULT 'United Kingdom'::character varying,
    status character varying(20) DEFAULT 'active'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.clinics OWNER TO celloxen_user;

--
-- Name: clinics_id_seq; Type: SEQUENCE; Schema: public; Owner: celloxen_user
--

CREATE SEQUENCE public.clinics_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.clinics_id_seq OWNER TO celloxen_user;

--
-- Name: clinics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: celloxen_user
--

ALTER SEQUENCE public.clinics_id_seq OWNED BY public.clinics.id;


--
-- Name: comprehensive_assessments; Type: TABLE; Schema: public; Owner: celloxen_user
--

CREATE TABLE public.comprehensive_assessments (
    id bigint NOT NULL,
    patient_id bigint NOT NULL,
    assessment_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    assessment_status character varying(20) DEFAULT 'in_progress'::character varying,
    questionnaire_responses jsonb,
    questionnaire_scores jsonb,
    questionnaire_recommendations jsonb,
    iridology_data jsonb,
    constitutional_type character varying(50),
    constitutional_strength character varying(20),
    iris_images jsonb,
    overall_wellness_score numeric(5,2),
    integrated_recommendations jsonb,
    comprehensive_report jsonb,
    practitioner_id bigint,
    assessment_duration_minutes integer,
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    questionnaire_completed boolean DEFAULT false,
    iridology_completed boolean DEFAULT false
);


ALTER TABLE public.comprehensive_assessments OWNER TO celloxen_user;

--
-- Name: TABLE comprehensive_assessments; Type: COMMENT; Schema: public; Owner: celloxen_user
--

COMMENT ON TABLE public.comprehensive_assessments IS 'Stores complete patient assessments combining questionnaire and iridology data';


--
-- Name: comprehensive_assessments_id_seq; Type: SEQUENCE; Schema: public; Owner: celloxen_user
--

CREATE SEQUENCE public.comprehensive_assessments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.comprehensive_assessments_id_seq OWNER TO celloxen_user;

--
-- Name: comprehensive_assessments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: celloxen_user
--

ALTER SEQUENCE public.comprehensive_assessments_id_seq OWNED BY public.comprehensive_assessments.id;


--
-- Name: contraindication_checks; Type: TABLE; Schema: public; Owner: celloxen_user
--

CREATE TABLE public.contraindication_checks (
    id integer NOT NULL,
    assessment_id bigint,
    patient_id bigint,
    heart_condition boolean DEFAULT false,
    pacemaker_fitted boolean DEFAULT false,
    pregnant boolean,
    contraindication_notes text,
    has_contraindications boolean DEFAULT false,
    checked_by bigint,
    checked_at timestamp without time zone DEFAULT now(),
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.contraindication_checks OWNER TO celloxen_user;

--
-- Name: contraindication_checks_id_seq; Type: SEQUENCE; Schema: public; Owner: celloxen_user
--

CREATE SEQUENCE public.contraindication_checks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.contraindication_checks_id_seq OWNER TO celloxen_user;

--
-- Name: contraindication_checks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: celloxen_user
--

ALTER SEQUENCE public.contraindication_checks_id_seq OWNED BY public.contraindication_checks.id;


--
-- Name: domain_followup_questions; Type: TABLE; Schema: public; Owner: celloxen_user
--

CREATE TABLE public.domain_followup_questions (
    id integer NOT NULL,
    domain character varying(50) NOT NULL,
    question_text text NOT NULL,
    question_order integer NOT NULL,
    severity_threshold numeric DEFAULT 3.5,
    active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.domain_followup_questions OWNER TO celloxen_user;

--
-- Name: domain_followup_questions_id_seq; Type: SEQUENCE; Schema: public; Owner: celloxen_user
--

CREATE SEQUENCE public.domain_followup_questions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.domain_followup_questions_id_seq OWNER TO celloxen_user;

--
-- Name: domain_followup_questions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: celloxen_user
--

ALTER SEQUENCE public.domain_followup_questions_id_seq OWNED BY public.domain_followup_questions.id;


--
-- Name: domain_followup_responses; Type: TABLE; Schema: public; Owner: celloxen_user
--

CREATE TABLE public.domain_followup_responses (
    id integer NOT NULL,
    assessment_id bigint,
    patient_id bigint,
    question_id integer,
    question_text text,
    response text NOT NULL,
    answered_at timestamp without time zone DEFAULT now(),
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.domain_followup_responses OWNER TO celloxen_user;

--
-- Name: domain_followup_responses_id_seq; Type: SEQUENCE; Schema: public; Owner: celloxen_user
--

CREATE SEQUENCE public.domain_followup_responses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.domain_followup_responses_id_seq OWNER TO celloxen_user;

--
-- Name: domain_followup_responses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: celloxen_user
--

ALTER SEQUENCE public.domain_followup_responses_id_seq OWNED BY public.domain_followup_responses.id;


--
-- Name: email_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.email_logs (
    id integer NOT NULL,
    patient_id integer,
    email_type character varying(50) NOT NULL,
    sent_to_email character varying(255) NOT NULL,
    subject character varying(500),
    status character varying(20) NOT NULL,
    sent_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    opened_at timestamp without time zone,
    clicked_at timestamp without time zone,
    error_message text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.email_logs OWNER TO postgres;

--
-- Name: TABLE email_logs; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.email_logs IS 'Tracks all email communications sent to patients';


--
-- Name: COLUMN email_logs.email_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.email_logs.email_type IS 'Type: INVITATION, ACCOUNT_CONFIRMATION, APPOINTMENT_CONFIRMATION, etc.';


--
-- Name: COLUMN email_logs.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.email_logs.status IS 'Status: SENT, FAILED, BOUNCED';


--
-- Name: email_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.email_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.email_logs_id_seq OWNER TO postgres;

--
-- Name: email_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.email_logs_id_seq OWNED BY public.email_logs.id;


--
-- Name: iridology_capture_sessions; Type: TABLE; Schema: public; Owner: celloxen_user
--

CREATE TABLE public.iridology_capture_sessions (
    id bigint NOT NULL,
    chatbot_session_id bigint NOT NULL,
    assessment_id bigint,
    left_eye_image_path character varying(500),
    left_eye_image_base64 text,
    left_eye_captured_at timestamp without time zone,
    left_eye_quality_score integer,
    left_eye_retakes integer DEFAULT 0,
    right_eye_image_path character varying(500),
    right_eye_image_base64 text,
    right_eye_captured_at timestamp without time zone,
    right_eye_quality_score integer,
    right_eye_retakes integer DEFAULT 0,
    ai_analysis_requested_at timestamp without time zone,
    ai_analysis_completed_at timestamp without time zone,
    ai_analysis_result jsonb,
    ai_analysis_duration_seconds integer,
    status character varying(20) DEFAULT 'in_progress'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.iridology_capture_sessions OWNER TO celloxen_user;

--
-- Name: iridology_capture_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: celloxen_user
--

CREATE SEQUENCE public.iridology_capture_sessions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.iridology_capture_sessions_id_seq OWNER TO celloxen_user;

--
-- Name: iridology_capture_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: celloxen_user
--

ALTER SEQUENCE public.iridology_capture_sessions_id_seq OWNED BY public.iridology_capture_sessions.id;


--
-- Name: iridology_findings; Type: TABLE; Schema: public; Owner: celloxen_user
--

CREATE TABLE public.iridology_findings (
    id bigint NOT NULL,
    assessment_id bigint NOT NULL,
    left_eye_constitutional character varying(20),
    right_eye_constitutional character varying(20),
    constitutional_notes text,
    digestive_system_condition character varying(20),
    circulatory_system_condition character varying(20),
    nervous_system_condition character varying(20),
    musculoskeletal_system_condition character varying(20),
    endocrine_system_condition character varying(20),
    iris_signs jsonb,
    primary_concerns text[],
    wellness_priorities text[],
    contraindications text[],
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.iridology_findings OWNER TO celloxen_user;

--
-- Name: TABLE iridology_findings; Type: COMMENT; Schema: public; Owner: celloxen_user
--

COMMENT ON TABLE public.iridology_findings IS 'Detailed iridology analysis results with constitutional typing and system assessments';


--
-- Name: iridology_findings_id_seq; Type: SEQUENCE; Schema: public; Owner: celloxen_user
--

CREATE SEQUENCE public.iridology_findings_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.iridology_findings_id_seq OWNER TO celloxen_user;

--
-- Name: iridology_findings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: celloxen_user
--

ALTER SEQUENCE public.iridology_findings_id_seq OWNED BY public.iridology_findings.id;


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: celloxen_user
--

CREATE TABLE public.notifications (
    id bigint NOT NULL,
    recipient_type public.recipienttype NOT NULL,
    recipient_id bigint NOT NULL,
    notification_type character varying(100) NOT NULL,
    channel public.notificationchannel NOT NULL,
    subject character varying(255),
    message text NOT NULL,
    related_entity_type character varying(50),
    related_entity_id bigint,
    status public.notificationstatus,
    sent_at timestamp with time zone,
    delivered_at timestamp with time zone,
    error_message text,
    retry_count integer,
    read boolean,
    read_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.notifications OWNER TO celloxen_user;

--
-- Name: notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: celloxen_user
--

CREATE SEQUENCE public.notifications_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.notifications_id_seq OWNER TO celloxen_user;

--
-- Name: notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: celloxen_user
--

ALTER SEQUENCE public.notifications_id_seq OWNED BY public.notifications.id;


--
-- Name: patients; Type: TABLE; Schema: public; Owner: celloxen_user
--

CREATE TABLE public.patients (
    id bigint NOT NULL,
    patient_number character varying(50) NOT NULL,
    clinic_id bigint NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    email character varying(255) NOT NULL,
    mobile_phone character varying(50) NOT NULL,
    date_of_birth date NOT NULL,
    status character varying(20) DEFAULT 'active'::character varying,
    portal_access boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    address text,
    emergency_contact character varying(100),
    emergency_phone character varying(20),
    medical_conditions text,
    medications text,
    allergies text,
    insurance_details text,
    notes text,
    password_hash character varying(255),
    registration_token character varying(255),
    token_expires_at timestamp without time zone,
    pre_assessment_completed boolean DEFAULT false
);


ALTER TABLE public.patients OWNER TO celloxen_user;

--
-- Name: patients_id_seq; Type: SEQUENCE; Schema: public; Owner: celloxen_user
--

CREATE SEQUENCE public.patients_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.patients_id_seq OWNER TO celloxen_user;

--
-- Name: patients_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: celloxen_user
--

ALTER SEQUENCE public.patients_id_seq OWNED BY public.patients.id;


--
-- Name: therapy_correlations; Type: TABLE; Schema: public; Owner: celloxen_user
--

CREATE TABLE public.therapy_correlations (
    id bigint NOT NULL,
    assessment_id bigint NOT NULL,
    therapy_code character varying(10) NOT NULL,
    questionnaire_priority character varying(20),
    iridology_priority character varying(20),
    combined_priority character varying(20),
    correlation_strength numeric(3,2),
    recommended boolean DEFAULT true,
    recommendation_reason text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.therapy_correlations OWNER TO celloxen_user;

--
-- Name: TABLE therapy_correlations; Type: COMMENT; Schema: public; Owner: celloxen_user
--

COMMENT ON TABLE public.therapy_correlations IS 'Tracks correlation between questionnaire results and iridology findings for therapy recommendations';


--
-- Name: therapy_correlations_id_seq; Type: SEQUENCE; Schema: public; Owner: celloxen_user
--

CREATE SEQUENCE public.therapy_correlations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.therapy_correlations_id_seq OWNER TO celloxen_user;

--
-- Name: therapy_correlations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: celloxen_user
--

ALTER SEQUENCE public.therapy_correlations_id_seq OWNED BY public.therapy_correlations.id;


--
-- Name: therapy_plan_items; Type: TABLE; Schema: public; Owner: celloxen_user
--

CREATE TABLE public.therapy_plan_items (
    id bigint NOT NULL,
    therapy_plan_id bigint NOT NULL,
    therapy_code character varying(20) NOT NULL,
    therapy_name character varying(255) NOT NULL,
    therapy_description text,
    recommended_sessions integer NOT NULL,
    session_duration_minutes integer,
    rationale text,
    target_domain public.therapydomain,
    priority public.therapypriority,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.therapy_plan_items OWNER TO celloxen_user;

--
-- Name: therapy_plan_items_id_seq; Type: SEQUENCE; Schema: public; Owner: celloxen_user
--

CREATE SEQUENCE public.therapy_plan_items_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.therapy_plan_items_id_seq OWNER TO celloxen_user;

--
-- Name: therapy_plan_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: celloxen_user
--

ALTER SEQUENCE public.therapy_plan_items_id_seq OWNED BY public.therapy_plan_items.id;


--
-- Name: therapy_plans; Type: TABLE; Schema: public; Owner: celloxen_user
--

CREATE TABLE public.therapy_plans (
    id bigint NOT NULL,
    plan_number character varying(50) NOT NULL,
    clinic_id bigint NOT NULL,
    patient_id bigint NOT NULL,
    assessment_id bigint NOT NULL,
    recommended_by bigint NOT NULL,
    status public.therapyplanstatus,
    patient_consent boolean,
    consent_date date,
    consent_signature text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    notes text
);


ALTER TABLE public.therapy_plans OWNER TO celloxen_user;

--
-- Name: therapy_plans_id_seq; Type: SEQUENCE; Schema: public; Owner: celloxen_user
--

CREATE SEQUENCE public.therapy_plans_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.therapy_plans_id_seq OWNER TO celloxen_user;

--
-- Name: therapy_plans_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: celloxen_user
--

ALTER SEQUENCE public.therapy_plans_id_seq OWNED BY public.therapy_plans.id;


--
-- Name: therapy_sessions; Type: TABLE; Schema: public; Owner: celloxen_user
--

CREATE TABLE public.therapy_sessions (
    id bigint NOT NULL,
    session_number character varying(50) NOT NULL,
    therapy_plan_item_id bigint NOT NULL,
    clinic_id bigint NOT NULL,
    patient_id bigint NOT NULL,
    session_sequence integer NOT NULL,
    total_sessions integer NOT NULL,
    scheduled_date date NOT NULL,
    scheduled_time time without time zone NOT NULL,
    duration_minutes integer,
    therapist_id bigint,
    status public.therapysessionstatus,
    checked_in_at timestamp with time zone,
    started_at timestamp with time zone,
    completed_at timestamp with time zone,
    therapy_settings json,
    therapist_notes text,
    patient_feedback text,
    any_concerns boolean,
    concern_details text,
    payment_status public.paymentstatus,
    payment_amount numeric(10,2),
    reminder_sent_48h boolean,
    reminder_sent_24h boolean,
    reminder_sent_2h boolean,
    completion_notification_sent boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    created_by bigint
);


ALTER TABLE public.therapy_sessions OWNER TO celloxen_user;

--
-- Name: therapy_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: celloxen_user
--

CREATE SEQUENCE public.therapy_sessions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.therapy_sessions_id_seq OWNER TO celloxen_user;

--
-- Name: therapy_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: celloxen_user
--

ALTER SEQUENCE public.therapy_sessions_id_seq OWNED BY public.therapy_sessions.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: celloxen_user
--

CREATE TABLE public.users (
    id bigint NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    full_name character varying(255) NOT NULL,
    role character varying(20) NOT NULL,
    clinic_id bigint,
    status character varying(20) DEFAULT 'active'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.users OWNER TO celloxen_user;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: celloxen_user
--

CREATE SEQUENCE public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO celloxen_user;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: celloxen_user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: appointments id; Type: DEFAULT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.appointments ALTER COLUMN id SET DEFAULT nextval('public.appointments_id_seq'::regclass);


--
-- Name: assessment_answers id; Type: DEFAULT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.assessment_answers ALTER COLUMN id SET DEFAULT nextval('public.assessment_answers_id_seq'::regclass);


--
-- Name: assessment_questions id; Type: DEFAULT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.assessment_questions ALTER COLUMN id SET DEFAULT nextval('public.assessment_questions_id_seq'::regclass);


--
-- Name: assessments id; Type: DEFAULT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.assessments ALTER COLUMN id SET DEFAULT nextval('public.assessments_id_seq'::regclass);


--
-- Name: audit_logs id; Type: DEFAULT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.audit_logs ALTER COLUMN id SET DEFAULT nextval('public.audit_logs_id_seq'::regclass);


--
-- Name: chatbot_messages id; Type: DEFAULT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.chatbot_messages ALTER COLUMN id SET DEFAULT nextval('public.chatbot_messages_id_seq'::regclass);


--
-- Name: chatbot_questions_progress id; Type: DEFAULT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.chatbot_questions_progress ALTER COLUMN id SET DEFAULT nextval('public.chatbot_questions_progress_id_seq'::regclass);


--
-- Name: chatbot_sessions id; Type: DEFAULT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.chatbot_sessions ALTER COLUMN id SET DEFAULT nextval('public.chatbot_sessions_id_seq'::regclass);


--
-- Name: clinics id; Type: DEFAULT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.clinics ALTER COLUMN id SET DEFAULT nextval('public.clinics_id_seq'::regclass);


--
-- Name: comprehensive_assessments id; Type: DEFAULT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.comprehensive_assessments ALTER COLUMN id SET DEFAULT nextval('public.comprehensive_assessments_id_seq'::regclass);


--
-- Name: contraindication_checks id; Type: DEFAULT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.contraindication_checks ALTER COLUMN id SET DEFAULT nextval('public.contraindication_checks_id_seq'::regclass);


--
-- Name: domain_followup_questions id; Type: DEFAULT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.domain_followup_questions ALTER COLUMN id SET DEFAULT nextval('public.domain_followup_questions_id_seq'::regclass);


--
-- Name: domain_followup_responses id; Type: DEFAULT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.domain_followup_responses ALTER COLUMN id SET DEFAULT nextval('public.domain_followup_responses_id_seq'::regclass);


--
-- Name: email_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_logs ALTER COLUMN id SET DEFAULT nextval('public.email_logs_id_seq'::regclass);


--
-- Name: iridology_capture_sessions id; Type: DEFAULT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.iridology_capture_sessions ALTER COLUMN id SET DEFAULT nextval('public.iridology_capture_sessions_id_seq'::regclass);


--
-- Name: iridology_findings id; Type: DEFAULT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.iridology_findings ALTER COLUMN id SET DEFAULT nextval('public.iridology_findings_id_seq'::regclass);


--
-- Name: notifications id; Type: DEFAULT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.notifications ALTER COLUMN id SET DEFAULT nextval('public.notifications_id_seq'::regclass);


--
-- Name: patients id; Type: DEFAULT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.patients ALTER COLUMN id SET DEFAULT nextval('public.patients_id_seq'::regclass);


--
-- Name: therapy_correlations id; Type: DEFAULT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.therapy_correlations ALTER COLUMN id SET DEFAULT nextval('public.therapy_correlations_id_seq'::regclass);


--
-- Name: therapy_plan_items id; Type: DEFAULT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.therapy_plan_items ALTER COLUMN id SET DEFAULT nextval('public.therapy_plan_items_id_seq'::regclass);


--
-- Name: therapy_plans id; Type: DEFAULT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.therapy_plans ALTER COLUMN id SET DEFAULT nextval('public.therapy_plans_id_seq'::regclass);


--
-- Name: therapy_sessions id; Type: DEFAULT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.therapy_sessions ALTER COLUMN id SET DEFAULT nextval('public.therapy_sessions_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: appointments; Type: TABLE DATA; Schema: public; Owner: celloxen_user
--

COPY public.appointments (id, appointment_number, clinic_id, patient_id, appointment_type, appointment_date, appointment_time, duration_minutes, practitioner_id, therapist_id, status, booking_notes, cancellation_reason, cancelled_at, cancelled_by, reminder_sent_24h, reminder_sent_2h, confirmation_sent, created_at, updated_at, created_by) FROM stdin;
1	APT-20251110022838	1	4	CONSULTATION	2025-10-15	10:30:00	60	\N	\N	CANCELLED	First Appointment	Cancelled by user	2025-11-14 03:14:29.120584+00	\N	\N	\N	\N	2025-11-10 02:28:38.847833+00	2025-11-14 03:14:29.120584+00	\N
2	APT-20251114033137	1	19	INITIAL_ASSESSMENT	2025-11-25	12:30:00	60	\N	\N	SCHEDULED	test	\N	\N	\N	\N	\N	\N	2025-11-14 03:31:37.745194+00	2025-11-14 03:31:37.745194+00	\N
3	APT-20251114033858	1	19	INITIAL_ASSESSMENT	2025-11-30	09:00:00	60	\N	\N	SCHEDULED		\N	\N	\N	\N	\N	\N	2025-11-14 03:38:58.506079+00	2025-11-14 03:38:58.506079+00	\N
\.


--
-- Data for Name: assessment_answers; Type: TABLE DATA; Schema: public; Owner: celloxen_user
--

COPY public.assessment_answers (id, assessment_id, question_id, answer_value, answer_text, score_contribution, created_at) FROM stdin;
\.


--
-- Data for Name: assessment_questions; Type: TABLE DATA; Schema: public; Owner: celloxen_user
--

COPY public.assessment_questions (id, therapy_domain, question_text, question_type, question_order, response_options, scoring_weight, is_active, created_at) FROM stdin;
\.


--
-- Data for Name: assessments; Type: TABLE DATA; Schema: public; Owner: celloxen_user
--

COPY public.assessments (id, assessment_number, clinic_id, patient_id, assessment_type, status, questionnaire_started_at, questionnaire_completed_at, total_questions, questions_answered, iridology_included, iridology_left_image, iridology_right_image, iridology_analysis_result, diabetics_score, chronic_pain_score, anxiety_stress_score, energy_vitality_score, overall_wellness_score, report_generated, report_pdf_path, report_generated_at, created_at, updated_at, created_by) FROM stdin;
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: celloxen_user
--

COPY public.audit_logs (id, user_id, user_email, user_role, clinic_id, action, entity_type, entity_id, old_values, new_values, changed_fields, ip_address, user_agent, request_path, request_method, description, audit_metadata, success, error_message, created_at) FROM stdin;
\.


--
-- Data for Name: chatbot_messages; Type: TABLE DATA; Schema: public; Owner: celloxen_user
--

COPY public.chatbot_messages (id, session_id, sender_type, sender_id, message_type, message_text, question_id, answer_value, answer_score, metadata, read_at, created_at) FROM stdin;
\.


--
-- Data for Name: chatbot_questions_progress; Type: TABLE DATA; Schema: public; Owner: celloxen_user
--

COPY public.chatbot_questions_progress (id, session_id, domain, question_key, question_text, response_value, response_score, asked_at, answered_at, notes, created_at) FROM stdin;
\.


--
-- Data for Name: chatbot_sessions; Type: TABLE DATA; Schema: public; Owner: celloxen_user
--

COPY public.chatbot_sessions (id, session_token, session_type, patient_id, practitioner_id, clinic_id, status, current_stage, questionnaire_reviewed, follow_up_questions_completed, left_eye_captured, right_eye_captured, ai_analysis_completed, assessment_id, session_data, started_at, completed_at, last_activity_at, duration_minutes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: clinics; Type: TABLE DATA; Schema: public; Owner: celloxen_user
--

COPY public.clinics (id, name, email, phone, address_line1, city, postcode, country, status, created_at) FROM stdin;
1	Aberdeen Wellness Centre	info@aberdeenwellness.co.uk	01224 123456	123 Union Street	Aberdeen	AB10 1AA	United Kingdom	active	2025-11-08 20:07:26.625225
\.


--
-- Data for Name: comprehensive_assessments; Type: TABLE DATA; Schema: public; Owner: celloxen_user
--

COPY public.comprehensive_assessments (id, patient_id, assessment_date, assessment_status, questionnaire_responses, questionnaire_scores, questionnaire_recommendations, iridology_data, constitutional_type, constitutional_strength, iris_images, overall_wellness_score, integrated_recommendations, comprehensive_report, practitioner_id, assessment_duration_minutes, notes, created_at, updated_at, questionnaire_completed, iridology_completed) FROM stdin;
2	18	2025-11-14 15:35:51.110705	completed	{"q1": {"score": 50, "answer": "Moderate"}, "q2": {"score": 25, "answer": "Daily"}, "q3": {"score": 0, "answer": "Always"}, "q4": {"score": 50, "answer": "Moderately"}, "q5": {"score": 25, "answer": "Foggy"}, "q6": {"score": 50, "answer": "6-7 hours"}, "q7": {"score": 25, "answer": "Rarely"}, "q8": {"score": 25, "answer": "Moderate-Severe"}, "q9": {"score": 75, "answer": "Slightly limits"}, "q10": {"score": 25, "answer": "Very stiff"}, "q11": {"score": 50, "answer": "Moderate"}, "q12": {"score": 25, "answer": "Daily"}, "q13": {"score": 50, "answer": "Manageable"}, "q14": {"score": 25, "answer": "Significantly"}, "q15": {"score": 25, "answer": "Very Often"}, "q16": {"score": 25, "answer": "Often"}, "q17": {"score": 50, "answer": "Moderate"}, "q18": {"score": 25, "answer": "Often"}, "q19": {"score": 50, "answer": "Sometimes"}, "q20": {"score": 25, "answer": "Poor"}, "q21": {"score": 50, "answer": "Sometimes"}, "q22": {"score": 0, "answer": "Extreme"}, "q23": {"score": 50, "answer": "Sometimes"}, "q24": {"score": 50, "answer": "Moderately"}, "q25": {"score": 50, "answer": "Fair"}, "q26": {"score": 50, "answer": "Sometimes"}, "q27": {"score": 50, "answer": "Moderate"}, "q28": {"score": 25, "answer": "Often"}, "q29": {"score": 50, "answer": "Weekly"}, "q30": {"score": 25, "answer": "Irregular"}, "q31": {"score": 50, "answer": "Occasionally"}, "q32": {"score": 25, "answer": "Slowly"}, "q33": {"score": 50, "answer": "A Few"}, "q34": {"score": 25, "answer": "Poor"}, "q35": {"score": 50, "answer": "Weekly"}}	{"vitality_energy": {"score": 32.1, "domain_name": "Vitality & Energy Support", "therapy_code": "C-102", "total_questions": 7, "questions_answered": 7}, "comfort_mobility": {"score": 39.3, "domain_name": "Comfort & Mobility Support", "therapy_code": "C-104", "total_questions": 7, "questions_answered": 7}, "immune_digestive": {"score": 39.3, "domain_name": "Immune & Digestive Wellness", "therapy_code": "C-108", "total_questions": 7, "questions_answered": 7}, "circulation_heart": {"score": 35.7, "domain_name": "Circulation & Heart Wellness", "therapy_code": "C-105", "total_questions": 7, "questions_answered": 7}, "stress_relaxation": {"score": 39.3, "domain_name": "Stress & Relaxation Support", "therapy_code": "C-107", "total_questions": 7, "questions_answered": 7}}	\N	\N	\N	\N	\N	37.10	\N	\N	\N	\N	\N	2025-11-14 15:34:48.49655	2025-11-14 15:35:51.110705	f	f
1	18	2025-11-14 15:31:54.915933	completed	{"q1": {"score": 25, "answer": "Low"}, "q2": {"score": 25, "answer": "Daily"}, "q3": {"score": 0, "answer": "Always"}, "q4": {"score": 25, "answer": "Poorly"}, "q5": {"score": 0, "answer": "Very Foggy"}, "q6": {"score": 50, "answer": "6-7 hours"}, "q7": {"score": 25, "answer": "Rarely"}, "q8": {"score": 50, "answer": "Moderate"}, "q9": {"score": 0, "answer": "Severely limits"}, "q10": {"score": 100, "answer": "Not stiff"}, "q11": {"score": 75, "answer": "Good"}, "q12": {"score": 50, "answer": "Few times a week"}, "q13": {"score": 25, "answer": "Difficult"}, "q14": {"score": 0, "answer": "Severely"}, "q15": {"score": 100, "answer": "Never"}, "q16": {"score": 75, "answer": "Rarely"}, "q17": {"score": 50, "answer": "Moderate"}, "q18": {"score": 25, "answer": "Often"}, "q19": {"score": 75, "answer": "Rarely"}, "q20": {"score": 50, "answer": "Fair"}, "q21": {"score": 25, "answer": "Often"}, "q22": {"score": 0, "answer": "Extreme"}, "q23": {"score": 50, "answer": "Sometimes"}, "q24": {"score": 75, "answer": "Well"}, "q25": {"score": 50, "answer": "Fair"}, "q26": {"score": 25, "answer": "Rarely"}, "q27": {"score": 0, "answer": "Very Difficult"}, "q28": {"score": 50, "answer": "Sometimes"}, "q29": {"score": 50, "answer": "Weekly"}, "q30": {"score": 75, "answer": "Regular"}, "q31": {"score": 50, "answer": "Occasionally"}, "q32": {"score": 25, "answer": "Slowly"}, "q33": {"score": 50, "answer": "A Few"}, "q34": {"score": 25, "answer": "Poor"}, "q35": {"score": 50, "answer": "Weekly"}}	{"vitality_energy": {"score": 21.4, "domain_name": "Vitality & Energy Support", "therapy_code": "C-102", "total_questions": 7, "questions_answered": 7}, "comfort_mobility": {"score": 42.9, "domain_name": "Comfort & Mobility Support", "therapy_code": "C-104", "total_questions": 7, "questions_answered": 7}, "immune_digestive": {"score": 46.4, "domain_name": "Immune & Digestive Wellness", "therapy_code": "C-108", "total_questions": 7, "questions_answered": 7}, "circulation_heart": {"score": 57.1, "domain_name": "Circulation & Heart Wellness", "therapy_code": "C-105", "total_questions": 7, "questions_answered": 7}, "stress_relaxation": {"score": 35.7, "domain_name": "Stress & Relaxation Support", "therapy_code": "C-107", "total_questions": 7, "questions_answered": 7}}	\N	\N	\N	\N	\N	40.70	\N	\N	\N	\N	\N	2025-11-14 15:30:52.432724	2025-11-14 15:31:54.915933	f	f
4	18	2025-11-14 17:12:28.030422	completed	{"q1": {"score": 75, "answer": "Good"}, "q2": {"score": 75, "answer": "Rarely"}, "q3": {"score": 50, "answer": "Sometimes"}, "q4": {"score": 50, "answer": "Moderately"}, "q5": {"score": 75, "answer": "Clear"}, "q6": {"score": 25, "answer": "5-6 hours"}, "q7": {"score": 50, "answer": "Sometimes"}, "q8": {"score": 25, "answer": "Moderate-Severe"}, "q9": {"score": 0, "answer": "Severely limits"}, "q10": {"score": 50, "answer": "Moderately stiff"}, "q11": {"score": 50, "answer": "Moderate"}, "q12": {"score": 25, "answer": "Daily"}, "q13": {"score": 50, "answer": "Manageable"}, "q14": {"score": 75, "answer": "Slightly"}, "q15": {"score": 25, "answer": "Very Often"}, "q16": {"score": 75, "answer": "Rarely"}, "q17": {"score": 25, "answer": "Very Limited"}, "q18": {"score": 0, "answer": "Very Often"}, "q19": {"score": 50, "answer": "Sometimes"}, "q20": {"score": 50, "answer": "Fair"}, "q21": {"score": 25, "answer": "Often"}, "q22": {"score": 0, "answer": "Extreme"}, "q23": {"score": 25, "answer": "Very Often"}, "q24": {"score": 50, "answer": "Moderately"}, "q25": {"score": 50, "answer": "Fair"}, "q26": {"score": 25, "answer": "Rarely"}, "q27": {"score": 50, "answer": "Moderate"}, "q28": {"score": 25, "answer": "Often"}, "q29": {"score": 25, "answer": "Several times a week"}, "q30": {"score": 50, "answer": "Somewhat Regular"}, "q31": {"score": 50, "answer": "Occasionally"}, "q32": {"score": 25, "answer": "Slowly"}, "q33": {"score": 25, "answer": "Several"}, "q34": {"score": 25, "answer": "Poor"}, "q35": {"score": 25, "answer": "Several times a week"}}	{"vitality_energy": {"score": 57.1, "domain_name": "Vitality & Energy Support", "therapy_code": "C-102", "total_questions": 7, "questions_answered": 7}, "comfort_mobility": {"score": 39.3, "domain_name": "Comfort & Mobility Support", "therapy_code": "C-104", "total_questions": 7, "questions_answered": 7}, "immune_digestive": {"score": 32.1, "domain_name": "Immune & Digestive Wellness", "therapy_code": "C-108", "total_questions": 7, "questions_answered": 7}, "circulation_heart": {"score": 35.7, "domain_name": "Circulation & Heart Wellness", "therapy_code": "C-105", "total_questions": 7, "questions_answered": 7}, "stress_relaxation": {"score": 32.1, "domain_name": "Stress & Relaxation Support", "therapy_code": "C-107", "total_questions": 7, "questions_answered": 7}}	\N	{"findings": {"vitality_energy": "Analysis in progress", "comfort_mobility": "Analysis in progress", "immune_digestive": "Analysis in progress", "circulation_heart": "Analysis in progress", "stress_relaxation": "Analysis in progress"}, "recommendations": ["Please consult with practitioner for detailed analysis"], "stress_indicators": ["Analysis pending"], "constitutional_type": "Analysis Pending", "constitutional_strength": "Moderate"}	Analysis Pending	Moderate	{"left_eye": "stored", "right_eye": "stored"}	39.30	\N	\N	\N	\N	\N	2025-11-14 17:10:53.193939	2025-11-14 17:12:28.030422	f	t
3	18	2025-11-14 16:58:32.171936	in_progress	{"q1": {"score": 25, "answer": "Low"}, "q2": {"score": 75, "answer": "Rarely"}, "q3": {"score": 100, "answer": "Never"}, "q4": {"score": 50, "answer": "Moderately"}, "q5": {"score": 25, "answer": "Foggy"}, "q6": {"score": 50, "answer": "6-7 hours"}, "q7": {"score": 25, "answer": "Rarely"}, "q8": {"score": 75, "answer": "Mild"}, "q9": {"score": 50, "answer": "Moderately limits"}, "q10": {"score": 0, "answer": "Extremely stiff"}, "q11": {"score": 50, "answer": "Moderate"}, "q12": {"score": 50, "answer": "Few times a week"}, "q13": {"score": 0, "answer": "Very Difficult"}, "q14": {"score": 50, "answer": "Moderately"}, "q15": {"score": 25, "answer": "Very Often"}, "q16": {"score": 25, "answer": "Often"}, "q17": {"score": 100, "answer": "Excellent"}, "q18": {"score": 50, "answer": "Sometimes"}, "q19": {"score": 50, "answer": "Sometimes"}, "q20": {"score": 25, "answer": "Poor"}, "q21": {"score": 75, "answer": "Rarely"}, "q22": {"score": 0, "answer": "Extreme"}, "q23": {"score": 75, "answer": "Rarely"}, "q24": {"score": 50, "answer": "Moderately"}, "q25": {"score": 0, "answer": "Very Poor"}, "q26": {"score": 50, "answer": "Sometimes"}, "q27": {"score": 100, "answer": "Very Easy"}, "q28": {"score": 0, "answer": "Very Often"}, "q29": {"score": 50, "answer": "Weekly"}, "q30": {"score": 25, "answer": "Irregular"}, "q31": {"score": 50, "answer": "Occasionally"}, "q32": {"score": 25, "answer": "Slowly"}, "q33": {"score": 50, "answer": "A Few"}, "q34": {"score": 25, "answer": "Poor"}, "q35": {"score": 50, "answer": "Weekly"}}	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-14 16:58:32.171936	2025-11-14 16:59:38.07719	f	f
5	17	2025-11-14 17:15:49.53632	completed	{"q1": {"score": 50, "answer": "Moderate"}, "q2": {"score": 50, "answer": "Few times a week"}, "q3": {"score": 75, "answer": "Rarely"}, "q4": {"score": 50, "answer": "Moderately"}, "q5": {"score": 50, "answer": "Average"}, "q6": {"score": 25, "answer": "5-6 hours"}, "q7": {"score": 25, "answer": "Rarely"}, "q8": {"score": 50, "answer": "Moderate"}, "q9": {"score": 75, "answer": "Slightly limits"}, "q10": {"score": 50, "answer": "Moderately stiff"}, "q11": {"score": 50, "answer": "Moderate"}, "q12": {"score": 75, "answer": "Rarely"}, "q13": {"score": 50, "answer": "Manageable"}, "q14": {"score": 50, "answer": "Moderately"}, "q15": {"score": 50, "answer": "Sometimes"}, "q16": {"score": 75, "answer": "Rarely"}, "q17": {"score": 25, "answer": "Very Limited"}, "q18": {"score": 50, "answer": "Sometimes"}, "q19": {"score": 50, "answer": "Sometimes"}, "q20": {"score": 25, "answer": "Poor"}, "q21": {"score": 50, "answer": "Sometimes"}, "q22": {"score": 50, "answer": "Moderate"}, "q23": {"score": 50, "answer": "Sometimes"}, "q24": {"score": 50, "answer": "Moderately"}, "q25": {"score": 25, "answer": "Poor"}, "q26": {"score": 25, "answer": "Rarely"}, "q27": {"score": 75, "answer": "Easy"}, "q28": {"score": 50, "answer": "Sometimes"}, "q29": {"score": 25, "answer": "Several times a week"}, "q30": {"score": 50, "answer": "Somewhat Regular"}, "q31": {"score": 50, "answer": "Occasionally"}, "q32": {"score": 25, "answer": "Slowly"}, "q33": {"score": 50, "answer": "A Few"}, "q34": {"score": 25, "answer": "Poor"}, "q35": {"score": 50, "answer": "Weekly"}}	{"vitality_energy": {"score": 46.4, "domain_name": "Vitality & Energy Support", "therapy_code": "C-102", "total_questions": 7, "questions_answered": 7}, "comfort_mobility": {"score": 57.1, "domain_name": "Comfort & Mobility Support", "therapy_code": "C-104", "total_questions": 7, "questions_answered": 7}, "immune_digestive": {"score": 39.3, "domain_name": "Immune & Digestive Wellness", "therapy_code": "C-108", "total_questions": 7, "questions_answered": 7}, "circulation_heart": {"score": 46.4, "domain_name": "Circulation & Heart Wellness", "therapy_code": "C-105", "total_questions": 7, "questions_answered": 7}, "stress_relaxation": {"score": 46.4, "domain_name": "Stress & Relaxation Support", "therapy_code": "C-107", "total_questions": 7, "questions_answered": 7}}	\N	{"findings": {"vitality_energy": "Analysis in progress", "comfort_mobility": "Analysis in progress", "immune_digestive": "Analysis in progress", "circulation_heart": "Analysis in progress", "stress_relaxation": "Analysis in progress"}, "recommendations": ["Please consult with practitioner for detailed analysis"], "stress_indicators": ["Analysis pending"], "constitutional_type": "Analysis Pending", "constitutional_strength": "Moderate"}	Analysis Pending	Moderate	{"left_eye": "stored", "right_eye": "stored"}	47.10	\N	\N	\N	\N	\N	2025-11-14 17:14:30.99039	2025-11-14 17:15:49.53632	f	t
6	18	2025-11-14 23:37:30.244321	completed	{"q1": {"score": 25, "answer": "Low"}, "q2": {"score": 50, "answer": "Few times a week"}, "q3": {"score": 75, "answer": "Rarely"}, "q4": {"score": 50, "answer": "Moderately"}, "q5": {"score": 25, "answer": "Foggy"}, "q6": {"score": 75, "answer": "7-8 hours"}, "q7": {"score": 50, "answer": "Sometimes"}, "q8": {"score": 25, "answer": "Moderate-Severe"}, "q9": {"score": 50, "answer": "Moderately limits"}, "q10": {"score": 100, "answer": "Not stiff"}, "q11": {"score": 50, "answer": "Moderate"}, "q12": {"score": 25, "answer": "Daily"}, "q13": {"score": 50, "answer": "Manageable"}, "q14": {"score": 50, "answer": "Moderately"}, "q15": {"score": 100, "answer": "Never"}, "q16": {"score": 50, "answer": "Sometimes"}, "q17": {"score": 25, "answer": "Very Limited"}, "q18": {"score": 50, "answer": "Sometimes"}, "q19": {"score": 75, "answer": "Rarely"}, "q20": {"score": 100, "answer": "Excellent"}, "q21": {"score": 50, "answer": "Sometimes"}, "q22": {"score": 50, "answer": "Moderate"}, "q23": {"score": 0, "answer": "Constantly"}, "q24": {"score": 50, "answer": "Moderately"}, "q25": {"score": 25, "answer": "Poor"}, "q26": {"score": 75, "answer": "Often"}, "q27": {"score": 25, "answer": "Difficult"}, "q28": {"score": 75, "answer": "Rarely"}, "q29": {"score": 50, "answer": "Weekly"}, "q30": {"score": 75, "answer": "Regular"}, "q31": {"score": 50, "answer": "Occasionally"}, "q32": {"score": 100, "answer": "Very Quickly"}, "q33": {"score": 100, "answer": "None"}, "q34": {"score": 0, "answer": "Very Poor"}, "q35": {"score": 75, "answer": "Rarely"}}	{"vitality_energy": {"score": 50.0, "domain_name": "Vitality & Energy Support", "therapy_code": "C-102", "total_questions": 7, "questions_answered": 7}, "comfort_mobility": {"score": 50.0, "domain_name": "Comfort & Mobility Support", "therapy_code": "C-104", "total_questions": 7, "questions_answered": 7}, "immune_digestive": {"score": 64.3, "domain_name": "Immune & Digestive Wellness", "therapy_code": "C-108", "total_questions": 7, "questions_answered": 7}, "circulation_heart": {"score": 64.3, "domain_name": "Circulation & Heart Wellness", "therapy_code": "C-105", "total_questions": 7, "questions_answered": 7}, "stress_relaxation": {"score": 42.9, "domain_name": "Stress & Relaxation Support", "therapy_code": "C-107", "total_questions": 7, "questions_answered": 7}}	\N	{"findings": {"vitality_energy": "Analysis in progress", "comfort_mobility": "Analysis in progress", "immune_digestive": "Analysis in progress", "circulation_heart": "Analysis in progress", "stress_relaxation": "Analysis in progress"}, "recommendations": ["Please consult with practitioner for detailed analysis"], "stress_indicators": ["Analysis pending"], "constitutional_type": "Analysis Pending", "constitutional_strength": "Moderate"}	Analysis Pending	Moderate	{"left_eye": "stored", "right_eye": "stored"}	54.30	\N	\N	\N	\N	\N	2025-11-14 23:35:40.232193	2025-11-14 23:37:30.244321	f	t
7	18	2025-11-14 23:41:39.334711	in_progress	{"q1": {"score": 75, "answer": "Good"}}	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-11-14 23:41:39.334711	2025-11-14 23:41:42.175241	f	f
8	19	2025-11-14 23:43:48.920487	completed	{"q1": {"score": 50, "answer": "Moderate"}, "q2": {"score": 50, "answer": "Few times a week"}, "q3": {"score": 75, "answer": "Rarely"}, "q4": {"score": 75, "answer": "Well"}, "q5": {"score": 75, "answer": "Clear"}, "q6": {"score": 50, "answer": "6-7 hours"}, "q7": {"score": 50, "answer": "Sometimes"}, "q8": {"score": 50, "answer": "Moderate"}, "q9": {"score": 50, "answer": "Moderately limits"}, "q10": {"score": 50, "answer": "Moderately stiff"}, "q11": {"score": 50, "answer": "Moderate"}, "q12": {"score": 50, "answer": "Few times a week"}, "q13": {"score": 75, "answer": "Easy"}, "q14": {"score": 50, "answer": "Moderately"}, "q15": {"score": 50, "answer": "Sometimes"}, "q16": {"score": 75, "answer": "Rarely"}, "q17": {"score": 25, "answer": "Very Limited"}, "q18": {"score": 50, "answer": "Sometimes"}, "q19": {"score": 50, "answer": "Sometimes"}, "q20": {"score": 50, "answer": "Fair"}, "q21": {"score": 75, "answer": "Rarely"}, "q22": {"score": 75, "answer": "Low"}, "q23": {"score": 75, "answer": "Rarely"}, "q24": {"score": 50, "answer": "Moderately"}, "q25": {"score": 50, "answer": "Fair"}, "q26": {"score": 100, "answer": "Always"}, "q27": {"score": 50, "answer": "Moderate"}, "q28": {"score": 100, "answer": "Never"}, "q29": {"score": 25, "answer": "Several times a week"}, "q30": {"score": 75, "answer": "Regular"}, "q31": {"score": 50, "answer": "Occasionally"}, "q32": {"score": 75, "answer": "Quickly"}, "q33": {"score": 50, "answer": "A Few"}, "q34": {"score": 25, "answer": "Poor"}, "q35": {"score": 50, "answer": "Weekly"}}	{"vitality_energy": {"score": 60.7, "domain_name": "Vitality & Energy Support", "therapy_code": "C-102", "total_questions": 7, "questions_answered": 7}, "comfort_mobility": {"score": 53.6, "domain_name": "Comfort & Mobility Support", "therapy_code": "C-104", "total_questions": 7, "questions_answered": 7}, "immune_digestive": {"score": 50.0, "domain_name": "Immune & Digestive Wellness", "therapy_code": "C-108", "total_questions": 7, "questions_answered": 7}, "circulation_heart": {"score": 53.6, "domain_name": "Circulation & Heart Wellness", "therapy_code": "C-105", "total_questions": 7, "questions_answered": 7}, "stress_relaxation": {"score": 71.4, "domain_name": "Stress & Relaxation Support", "therapy_code": "C-107", "total_questions": 7, "questions_answered": 7}}	\N	{"findings": {"vitality_energy": "Analysis in progress", "comfort_mobility": "Analysis in progress", "immune_digestive": "Analysis in progress", "circulation_heart": "Analysis in progress", "stress_relaxation": "Analysis in progress"}, "recommendations": ["Please consult with practitioner for detailed analysis"], "stress_indicators": ["Analysis pending"], "constitutional_type": "Analysis Pending", "constitutional_strength": "Moderate"}	Analysis Pending	Moderate	{"left_eye": "stored", "right_eye": "stored"}	57.90	\N	\N	\N	\N	\N	2025-11-14 23:41:56.134169	2025-11-14 23:43:48.920487	f	t
9	17	2025-11-15 00:22:20.201149	questionnaire_only	{"c1": "Sometimes", "c2": "High", "c3": "Sometimes", "c4": "Moderate", "d1": "Rarely", "d2": "Regular and comfortable", "d3": "Rarely", "d4": "Low appetite", "i1": "Sometimes (3-4/year)", "i2": "Severe allergies", "i3": "Very slowly", "i4": "Chronically", "m1": "Sometimes", "m2": "Limited", "m3": "Sometimes", "m4": "Moderate", "n1": "Moderate", "n2": "Very poor - chronic insomnia", "n3": "Sometimes", "n4": "Moderate"}	{}	{}	\N	\N	\N	\N	0.00	[]	\N	\N	\N	\N	2025-11-15 00:22:20.201149	2025-11-15 00:22:20.201149	f	f
10	17	2025-11-15 00:22:24.977009	questionnaire_only	{"c1": "Sometimes", "c2": "High", "c3": "Sometimes", "c4": "Moderate", "d1": "Rarely", "d2": "Regular and comfortable", "d3": "Rarely", "d4": "Low appetite", "i1": "Sometimes (3-4/year)", "i2": "Severe allergies", "i3": "Very slowly", "i4": "Chronically", "m1": "Sometimes", "m2": "Limited", "m3": "Sometimes", "m4": "Moderate", "n1": "Moderate", "n2": "Very poor - chronic insomnia", "n3": "Sometimes", "n4": "Moderate"}	{}	{}	\N	\N	\N	\N	0.00	[]	\N	\N	\N	\N	2025-11-15 00:22:24.977009	2025-11-15 00:22:24.977009	f	f
11	17	2025-11-15 00:22:25.734304	questionnaire_only	{"c1": "Sometimes", "c2": "High", "c3": "Sometimes", "c4": "Moderate", "d1": "Rarely", "d2": "Regular and comfortable", "d3": "Rarely", "d4": "Low appetite", "i1": "Sometimes (3-4/year)", "i2": "Severe allergies", "i3": "Very slowly", "i4": "Chronically", "m1": "Sometimes", "m2": "Limited", "m3": "Sometimes", "m4": "Moderate", "n1": "Moderate", "n2": "Very poor - chronic insomnia", "n3": "Sometimes", "n4": "Moderate"}	{}	{}	\N	\N	\N	\N	0.00	[]	\N	\N	\N	\N	2025-11-15 00:22:25.734304	2025-11-15 00:22:25.734304	f	f
\.


--
-- Data for Name: contraindication_checks; Type: TABLE DATA; Schema: public; Owner: celloxen_user
--

COPY public.contraindication_checks (id, assessment_id, patient_id, heart_condition, pacemaker_fitted, pregnant, contraindication_notes, has_contraindications, checked_by, checked_at, created_at) FROM stdin;
\.


--
-- Data for Name: domain_followup_questions; Type: TABLE DATA; Schema: public; Owner: celloxen_user
--

COPY public.domain_followup_questions (id, domain, question_text, question_order, severity_threshold, active, created_at) FROM stdin;
1	energy	How would you describe your energy levels throughout the day? (e.g., constant fatigue, afternoon crashes, or generally good)	1	3.5	t	2025-11-13 08:30:05.047549
2	energy	Do you experience extreme tiredness or exhaustion that doesn't improve with rest?	2	3.5	t	2025-11-13 08:30:05.047549
3	energy	How is your mental clarity and ability to focus on tasks?	3	3.5	t	2025-11-13 08:30:05.047549
4	energy	Do you feel physically weak or have difficulty with normal daily activities?	4	3.5	t	2025-11-13 08:30:05.047549
5	energy	Have you noticed any changes in your energy levels over the past 3-6 months?	5	3.5	t	2025-11-13 08:30:05.047549
6	sleep	How many hours of sleep do you typically get per night?	1	3.5	t	2025-11-13 08:30:05.048624
7	sleep	Do you have difficulty falling asleep, or does it take more than 30 minutes?	2	3.5	t	2025-11-13 08:30:05.048624
8	sleep	Do you wake up during the night? If yes, how many times?	3	3.5	t	2025-11-13 08:30:05.048624
9	sleep	Do you wake feeling rested and refreshed, or still tired?	4	3.5	t	2025-11-13 08:30:05.048624
10	sleep	Do you experience daytime sleepiness or need to nap during the day?	5	3.5	t	2025-11-13 08:30:05.048624
11	stress	How often do you feel stressed or anxious? (daily, weekly, occasionally)	1	3.5	t	2025-11-13 08:30:05.049176
12	stress	Do you experience physical symptoms of stress such as headaches, muscle tension, or stomach issues?	2	3.5	t	2025-11-13 08:30:05.049176
13	stress	How well are you able to relax or unwind after stressful situations?	3	3.5	t	2025-11-13 08:30:05.049176
14	stress	Do you feel overwhelmed by daily responsibilities or tasks?	4	3.5	t	2025-11-13 08:30:05.049176
15	stress	How would you rate your overall mood and emotional wellbeing?	5	3.5	t	2025-11-13 08:30:05.049176
\.


--
-- Data for Name: domain_followup_responses; Type: TABLE DATA; Schema: public; Owner: celloxen_user
--

COPY public.domain_followup_responses (id, assessment_id, patient_id, question_id, question_text, response, answered_at, created_at) FROM stdin;
\.


--
-- Data for Name: email_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.email_logs (id, patient_id, email_type, sent_to_email, subject, status, sent_at, opened_at, clicked_at, error_message, created_at) FROM stdin;
1	4	INVITATION	a.kasem@welshdale.com	Welcome to Your Wellness Journey with Celloxen	SENT	2025-11-11 02:07:52.273209	\N	\N	\N	2025-11-11 02:07:52.273298
2	4	ACCOUNT_CONFIRMATION	a.kasem@welshdale.com	Your Celloxen Account is Ready!	SENT	2025-11-11 02:09:32.272171	\N	\N	\N	2025-11-11 02:09:32.272273
3	2	INVITATION	hafsarguib@yahoo.fr	Welcome to Your Wellness Journey with Celloxen	SENT	2025-11-11 16:22:52.011421	\N	\N	\N	2025-11-11 16:22:52.011552
4	2	ACCOUNT_CONFIRMATION	hafsarguib@yahoo.fr	Your Celloxen Account is Ready!	SENT	2025-11-11 16:33:34.312174	\N	\N	\N	2025-11-11 16:33:34.312278
5	12	INVITATION	raedzourob72@gmail.com	Welcome to Your Wellness Journey with Celloxen	SENT	2025-11-11 16:44:46.722461	\N	\N	\N	2025-11-11 16:44:46.722551
6	16	INVITATION	ztawfiq@hotmail.com	Welcome to Your Wellness Journey with Celloxen	SENT	2025-11-11 17:02:08.67192	\N	\N	\N	2025-11-11 17:02:08.672103
7	15	INVITATION	paul@ktpuk.co.uk	Welcome to Your Wellness Journey with Celloxen	SENT	2025-11-11 17:02:14.446446	\N	\N	\N	2025-11-11 17:02:14.446546
8	14	INVITATION	mattyrobey@hotmail.com	Welcome to Your Wellness Journey with Celloxen	SENT	2025-11-11 17:02:19.639186	\N	\N	\N	2025-11-11 17:02:19.639456
9	13	INVITATION	darrenrobey1972@gmail.com	Welcome to Your Wellness Journey with Celloxen	SENT	2025-11-11 17:02:24.042755	\N	\N	\N	2025-11-11 17:02:24.042871
10	16	ACCOUNT_CONFIRMATION	ztawfiq@hotmail.com	Your Celloxen Account is Ready!	SENT	2025-11-11 20:17:13.677004	\N	\N	\N	2025-11-11 20:17:13.677109
11	13	ACCOUNT_CONFIRMATION	darrenrobey1972@gmail.com	Your Celloxen Account is Ready!	SENT	2025-11-11 21:02:51.411591	\N	\N	\N	2025-11-11 21:02:51.411687
12	18	INVITATION	pay@welshdale.com	Welcome to Your Wellness Journey with Celloxen	SENT	2025-11-12 20:04:08.177582	\N	\N	\N	2025-11-12 20:04:08.17772
13	18	ACCOUNT_CONFIRMATION	pay@welshdale.com	Your Celloxen Account is Ready!	SENT	2025-11-12 20:05:38.030883	\N	\N	\N	2025-11-12 20:05:38.031007
\.


--
-- Data for Name: iridology_capture_sessions; Type: TABLE DATA; Schema: public; Owner: celloxen_user
--

COPY public.iridology_capture_sessions (id, chatbot_session_id, assessment_id, left_eye_image_path, left_eye_image_base64, left_eye_captured_at, left_eye_quality_score, left_eye_retakes, right_eye_image_path, right_eye_image_base64, right_eye_captured_at, right_eye_quality_score, right_eye_retakes, ai_analysis_requested_at, ai_analysis_completed_at, ai_analysis_result, ai_analysis_duration_seconds, status, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: iridology_findings; Type: TABLE DATA; Schema: public; Owner: celloxen_user
--

COPY public.iridology_findings (id, assessment_id, left_eye_constitutional, right_eye_constitutional, constitutional_notes, digestive_system_condition, circulatory_system_condition, nervous_system_condition, musculoskeletal_system_condition, endocrine_system_condition, iris_signs, primary_concerns, wellness_priorities, contraindications, created_at) FROM stdin;
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: celloxen_user
--

COPY public.notifications (id, recipient_type, recipient_id, notification_type, channel, subject, message, related_entity_type, related_entity_id, status, sent_at, delivered_at, error_message, retry_count, read, read_at, created_at) FROM stdin;
\.


--
-- Data for Name: patients; Type: TABLE DATA; Schema: public; Owner: celloxen_user
--

COPY public.patients (id, patient_number, clinic_id, first_name, last_name, email, mobile_phone, date_of_birth, status, portal_access, created_at, address, emergency_contact, emergency_phone, medical_conditions, medications, allergies, insurance_details, notes, password_hash, registration_token, token_expires_at, pre_assessment_completed) FROM stdin;
15	CLX-ABD-00008	1	Paul	Watkins	paul@ktpuk.co.uk	07970603777	1980-08-04	INVITED	t	2025-11-11 17:00:21.58091									\N	MJFdpLLJ9R45KspgVjjvZVxU9LBfZysy	2025-11-18 17:02:13.994012	f
14	CLX-ABD-00007	1	Matt	Robey	mattyrobey@hotmail.com	07890596715	1980-08-03	INVITED	t	2025-11-11 16:58:28.870836									\N	72UjuaF705Af8lD5r2Pa2fKeBYhG4I62	2025-11-18 17:02:19.199414	f
16	CLX-ABD-00009	1	Ziad 	Husien	ztawfiq@hotmail.com	07787790790	1959-01-22	active	t	2025-11-11 17:02:04.333494									$2b$12$nERUJcZaoHFbZ.wX74jMn.QO/7oJQCAeVLb7M.Q6GIfpBEq7msdWu	\N	\N	f
13	CLX-ABD-00006	1	Darren  	Robey	darrenrobey1972@gmail.com	07837648413	1972-10-15	active	t	2025-11-11 16:56:02.322522									$2b$12$Tpvz681Mpm4ZoFjzAv4oFegC7pZf2CIlAv4ObKt2einuEktmZUvcS	\N	\N	f
1	CLX-ABD-00001	1	Abid	Kasem	welshdale10@gmail.com	07700 123456	1975-06-15	active	t	2025-11-08 20:07:26.629008									$2b$12$oeIuqSaY7iOq/zv.5CKg7ePbKjzYUd3BTWG4mhRXJpj3djjEjDQ1.	\N	\N	f
17	CLX-ABD-00010	1	Bassam	Khalil	basabukhalil@gmail.com	0800766626562	1976-01-01	active	t	2025-11-12 13:05:32.180709									\N	\N	\N	f
5	P202511109840	1	Finally	Working	health@celloxen.com	07393960664	1970-01-01	INVITED	t	2025-11-10 23:46:28.686615	\N	\N	\N	\N	\N	\N	\N	\N	$2b$12$VSQNwcWTE607O5EBhLUDr.z.E7ILfFuWPzBMl4i1REseV6ls9eH6y	BH6ynmfWIXqra4QpX7yntFco3TLW9i8y	2025-11-18 02:02:24.273239	f
4	CLX-ABD-00003	1	Sam	Naqvi	a.kasem@welshdale.com	0739383838833	1960-01-01	active	t	2025-11-08 22:31:26.770509	123 High Street , Manchester, M1 2LU	John Raggi	0800655999	blood pressure	A|b6555	NONE		Anxiety	$2b$12$oIWWnD4hSv6RxCycWlEiHeUwjAVSPATjoEOshZ0Ujue5sOIwRaK4C	\N	\N	f
2	CLX-ABD-00002	1	Hafsa	Rguib	hafsarguib@yahoo.fr	7375308687	1981-09-30	active	t	2025-11-08 22:08:15.39508	\N	\N	\N	\N	\N	\N	\N	\N	$2b$12$fruGa1NECvPYU3m5gjKao.n6QUusLLHLVLr/KtMzbWsXib4eoZzBK	\N	\N	f
12	CLX-ABD-00005	1	RAED	 ZOUROB	raedzourob72@gmail.com	07393838838	1980-02-01	INVITED	t	2025-11-11 16:40:33.876939									\N	1T401ryub4xKqJHtPH5Uqlje6W4mnWeG	2025-11-18 16:44:46.219499	f
18	CLX-ABD-00011	1	Jack 	Dummy	pay@welshdale.com	0800900900	1990-01-01	active	t	2025-11-12 20:01:41.770524	2 High Street, Newmachar. Aberdeen, AB15 9HH	Susan Roomy	0800600901	High Blood Pressure, Diabetic 	Rampil, Omaparazol, Metformin 	Asprin			$2b$12$EKq9UkJgTJWXkw1IympqIuV9Pfyh1kPFnYL49ulCyvplyMJDXjAt2	\N	\N	f
19	CLX-ABD-00012	1	 TestStep1	Verification	lcruk@hotmail.com	07900000001	1995-01-01	active	t	2025-11-14 03:05:44.558914	Test Address, Aberdeen								\N	\N	\N	f
20	CLX-ABD-00013	1	test	smith	info@test.com	09008373737	1999-11-01	active	f	2025-11-14 03:45:41.704317	123 high street Leeds								\N	\N	\N	f
\.


--
-- Data for Name: therapy_correlations; Type: TABLE DATA; Schema: public; Owner: celloxen_user
--

COPY public.therapy_correlations (id, assessment_id, therapy_code, questionnaire_priority, iridology_priority, combined_priority, correlation_strength, recommended, recommendation_reason, created_at) FROM stdin;
\.


--
-- Data for Name: therapy_plan_items; Type: TABLE DATA; Schema: public; Owner: celloxen_user
--

COPY public.therapy_plan_items (id, therapy_plan_id, therapy_code, therapy_name, therapy_description, recommended_sessions, session_duration_minutes, rationale, target_domain, priority, created_at) FROM stdin;
\.


--
-- Data for Name: therapy_plans; Type: TABLE DATA; Schema: public; Owner: celloxen_user
--

COPY public.therapy_plans (id, plan_number, clinic_id, patient_id, assessment_id, recommended_by, status, patient_consent, consent_date, consent_signature, created_at, updated_at, notes) FROM stdin;
\.


--
-- Data for Name: therapy_sessions; Type: TABLE DATA; Schema: public; Owner: celloxen_user
--

COPY public.therapy_sessions (id, session_number, therapy_plan_item_id, clinic_id, patient_id, session_sequence, total_sessions, scheduled_date, scheduled_time, duration_minutes, therapist_id, status, checked_in_at, started_at, completed_at, therapy_settings, therapist_notes, patient_feedback, any_concerns, concern_details, payment_status, payment_amount, reminder_sent_48h, reminder_sent_24h, reminder_sent_2h, completion_notification_sent, created_at, updated_at, created_by) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: celloxen_user
--

COPY public.users (id, email, password_hash, full_name, role, clinic_id, status, created_at) FROM stdin;
1	admin@celloxen.com	$2b$12$yIHJWCBz6uTZcDP3h2xT1u9t1ylmq3t.E1azFp3R8HmkQnGp7g8W.	Celloxen Admin	super_admin	\N	active	2025-11-08 20:07:26.626769
2	staff@aberdeenwellness.co.uk	$2b$12$zey3vImlkbC8IWo8HO8U8ebahFr7RDOtyUY9v0.T0ascBFi4IUbY.	Aberdeen Clinic Staff	clinic_user	1	active	2025-11-08 20:07:26.627947
\.


--
-- Name: appointments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: celloxen_user
--

SELECT pg_catalog.setval('public.appointments_id_seq', 3, true);


--
-- Name: assessment_answers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: celloxen_user
--

SELECT pg_catalog.setval('public.assessment_answers_id_seq', 1, false);


--
-- Name: assessment_questions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: celloxen_user
--

SELECT pg_catalog.setval('public.assessment_questions_id_seq', 1, false);


--
-- Name: assessments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: celloxen_user
--

SELECT pg_catalog.setval('public.assessments_id_seq', 1, false);


--
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: celloxen_user
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 1, false);


--
-- Name: chatbot_messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: celloxen_user
--

SELECT pg_catalog.setval('public.chatbot_messages_id_seq', 1, false);


--
-- Name: chatbot_questions_progress_id_seq; Type: SEQUENCE SET; Schema: public; Owner: celloxen_user
--

SELECT pg_catalog.setval('public.chatbot_questions_progress_id_seq', 1, false);


--
-- Name: chatbot_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: celloxen_user
--

SELECT pg_catalog.setval('public.chatbot_sessions_id_seq', 1, false);


--
-- Name: clinics_id_seq; Type: SEQUENCE SET; Schema: public; Owner: celloxen_user
--

SELECT pg_catalog.setval('public.clinics_id_seq', 1, true);


--
-- Name: comprehensive_assessments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: celloxen_user
--

SELECT pg_catalog.setval('public.comprehensive_assessments_id_seq', 11, true);


--
-- Name: contraindication_checks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: celloxen_user
--

SELECT pg_catalog.setval('public.contraindication_checks_id_seq', 1, false);


--
-- Name: domain_followup_questions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: celloxen_user
--

SELECT pg_catalog.setval('public.domain_followup_questions_id_seq', 15, true);


--
-- Name: domain_followup_responses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: celloxen_user
--

SELECT pg_catalog.setval('public.domain_followup_responses_id_seq', 1, false);


--
-- Name: email_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.email_logs_id_seq', 13, true);


--
-- Name: iridology_capture_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: celloxen_user
--

SELECT pg_catalog.setval('public.iridology_capture_sessions_id_seq', 1, false);


--
-- Name: iridology_findings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: celloxen_user
--

SELECT pg_catalog.setval('public.iridology_findings_id_seq', 1, false);


--
-- Name: notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: celloxen_user
--

SELECT pg_catalog.setval('public.notifications_id_seq', 1, false);


--
-- Name: patients_id_seq; Type: SEQUENCE SET; Schema: public; Owner: celloxen_user
--

SELECT pg_catalog.setval('public.patients_id_seq', 20, true);


--
-- Name: therapy_correlations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: celloxen_user
--

SELECT pg_catalog.setval('public.therapy_correlations_id_seq', 1, false);


--
-- Name: therapy_plan_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: celloxen_user
--

SELECT pg_catalog.setval('public.therapy_plan_items_id_seq', 1, false);


--
-- Name: therapy_plans_id_seq; Type: SEQUENCE SET; Schema: public; Owner: celloxen_user
--

SELECT pg_catalog.setval('public.therapy_plans_id_seq', 1, false);


--
-- Name: therapy_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: celloxen_user
--

SELECT pg_catalog.setval('public.therapy_sessions_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: celloxen_user
--

SELECT pg_catalog.setval('public.users_id_seq', 2, true);


--
-- Name: appointments appointments_appointment_number_key; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_appointment_number_key UNIQUE (appointment_number);


--
-- Name: appointments appointments_pkey; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_pkey PRIMARY KEY (id);


--
-- Name: assessment_answers assessment_answers_pkey; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.assessment_answers
    ADD CONSTRAINT assessment_answers_pkey PRIMARY KEY (id);


--
-- Name: assessment_questions assessment_questions_pkey; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.assessment_questions
    ADD CONSTRAINT assessment_questions_pkey PRIMARY KEY (id);


--
-- Name: assessments assessments_assessment_number_key; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.assessments
    ADD CONSTRAINT assessments_assessment_number_key UNIQUE (assessment_number);


--
-- Name: assessments assessments_pkey; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.assessments
    ADD CONSTRAINT assessments_pkey PRIMARY KEY (id);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: chatbot_messages chatbot_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.chatbot_messages
    ADD CONSTRAINT chatbot_messages_pkey PRIMARY KEY (id);


--
-- Name: chatbot_questions_progress chatbot_questions_progress_pkey; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.chatbot_questions_progress
    ADD CONSTRAINT chatbot_questions_progress_pkey PRIMARY KEY (id);


--
-- Name: chatbot_sessions chatbot_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.chatbot_sessions
    ADD CONSTRAINT chatbot_sessions_pkey PRIMARY KEY (id);


--
-- Name: chatbot_sessions chatbot_sessions_session_token_key; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.chatbot_sessions
    ADD CONSTRAINT chatbot_sessions_session_token_key UNIQUE (session_token);


--
-- Name: clinics clinics_pkey; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.clinics
    ADD CONSTRAINT clinics_pkey PRIMARY KEY (id);


--
-- Name: comprehensive_assessments comprehensive_assessments_pkey; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.comprehensive_assessments
    ADD CONSTRAINT comprehensive_assessments_pkey PRIMARY KEY (id);


--
-- Name: contraindication_checks contraindication_checks_pkey; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.contraindication_checks
    ADD CONSTRAINT contraindication_checks_pkey PRIMARY KEY (id);


--
-- Name: domain_followup_questions domain_followup_questions_pkey; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.domain_followup_questions
    ADD CONSTRAINT domain_followup_questions_pkey PRIMARY KEY (id);


--
-- Name: domain_followup_responses domain_followup_responses_pkey; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.domain_followup_responses
    ADD CONSTRAINT domain_followup_responses_pkey PRIMARY KEY (id);


--
-- Name: email_logs email_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_logs
    ADD CONSTRAINT email_logs_pkey PRIMARY KEY (id);


--
-- Name: iridology_capture_sessions iridology_capture_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.iridology_capture_sessions
    ADD CONSTRAINT iridology_capture_sessions_pkey PRIMARY KEY (id);


--
-- Name: iridology_findings iridology_findings_pkey; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.iridology_findings
    ADD CONSTRAINT iridology_findings_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: patients patients_email_key; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.patients
    ADD CONSTRAINT patients_email_key UNIQUE (email);


--
-- Name: patients patients_patient_number_key; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.patients
    ADD CONSTRAINT patients_patient_number_key UNIQUE (patient_number);


--
-- Name: patients patients_pkey; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.patients
    ADD CONSTRAINT patients_pkey PRIMARY KEY (id);


--
-- Name: patients patients_registration_token_key; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.patients
    ADD CONSTRAINT patients_registration_token_key UNIQUE (registration_token);


--
-- Name: therapy_correlations therapy_correlations_pkey; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.therapy_correlations
    ADD CONSTRAINT therapy_correlations_pkey PRIMARY KEY (id);


--
-- Name: therapy_plan_items therapy_plan_items_pkey; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.therapy_plan_items
    ADD CONSTRAINT therapy_plan_items_pkey PRIMARY KEY (id);


--
-- Name: therapy_plans therapy_plans_pkey; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.therapy_plans
    ADD CONSTRAINT therapy_plans_pkey PRIMARY KEY (id);


--
-- Name: therapy_plans therapy_plans_plan_number_key; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.therapy_plans
    ADD CONSTRAINT therapy_plans_plan_number_key UNIQUE (plan_number);


--
-- Name: therapy_sessions therapy_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.therapy_sessions
    ADD CONSTRAINT therapy_sessions_pkey PRIMARY KEY (id);


--
-- Name: therapy_sessions therapy_sessions_session_number_key; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.therapy_sessions
    ADD CONSTRAINT therapy_sessions_session_number_key UNIQUE (session_number);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_assessment_questions_domain; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX idx_assessment_questions_domain ON public.assessment_questions USING btree (therapy_domain);


--
-- Name: idx_chatbot_messages_created; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX idx_chatbot_messages_created ON public.chatbot_messages USING btree (created_at DESC);


--
-- Name: idx_chatbot_messages_session; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX idx_chatbot_messages_session ON public.chatbot_messages USING btree (session_id);


--
-- Name: idx_chatbot_questions_domain; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX idx_chatbot_questions_domain ON public.chatbot_questions_progress USING btree (domain);


--
-- Name: idx_chatbot_questions_session; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX idx_chatbot_questions_session ON public.chatbot_questions_progress USING btree (session_id);


--
-- Name: idx_chatbot_sessions_patient; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX idx_chatbot_sessions_patient ON public.chatbot_sessions USING btree (patient_id);


--
-- Name: idx_chatbot_sessions_practitioner; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX idx_chatbot_sessions_practitioner ON public.chatbot_sessions USING btree (practitioner_id);


--
-- Name: idx_chatbot_sessions_status; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX idx_chatbot_sessions_status ON public.chatbot_sessions USING btree (status);


--
-- Name: idx_chatbot_sessions_token; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX idx_chatbot_sessions_token ON public.chatbot_sessions USING btree (session_token);


--
-- Name: idx_comp_assessments_date; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX idx_comp_assessments_date ON public.comprehensive_assessments USING btree (assessment_date);


--
-- Name: idx_comp_assessments_patient; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX idx_comp_assessments_patient ON public.comprehensive_assessments USING btree (patient_id);


--
-- Name: idx_comp_assessments_status; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX idx_comp_assessments_status ON public.comprehensive_assessments USING btree (assessment_status);


--
-- Name: idx_contraindication_assessment; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX idx_contraindication_assessment ON public.contraindication_checks USING btree (assessment_id);


--
-- Name: idx_email_logs_patient; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_email_logs_patient ON public.email_logs USING btree (patient_id);


--
-- Name: idx_email_logs_sent_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_email_logs_sent_at ON public.email_logs USING btree (sent_at);


--
-- Name: idx_email_logs_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_email_logs_status ON public.email_logs USING btree (status);


--
-- Name: idx_email_logs_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_email_logs_type ON public.email_logs USING btree (email_type);


--
-- Name: idx_followup_responses_assessment; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX idx_followup_responses_assessment ON public.domain_followup_responses USING btree (assessment_id);


--
-- Name: idx_iridology_capture_assessment; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX idx_iridology_capture_assessment ON public.iridology_capture_sessions USING btree (assessment_id);


--
-- Name: idx_iridology_capture_session; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX idx_iridology_capture_session ON public.iridology_capture_sessions USING btree (chatbot_session_id);


--
-- Name: idx_iridology_findings_assessment; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX idx_iridology_findings_assessment ON public.iridology_findings USING btree (assessment_id);


--
-- Name: idx_patients_email; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX idx_patients_email ON public.patients USING btree (lower((email)::text));


--
-- Name: idx_patients_token; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX idx_patients_token ON public.patients USING btree (registration_token);


--
-- Name: idx_therapy_correlations_assessment; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX idx_therapy_correlations_assessment ON public.therapy_correlations USING btree (assessment_id);


--
-- Name: ix_appointments_id; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX ix_appointments_id ON public.appointments USING btree (id);


--
-- Name: ix_assessment_answers_id; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX ix_assessment_answers_id ON public.assessment_answers USING btree (id);


--
-- Name: ix_assessments_id; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX ix_assessments_id ON public.assessments USING btree (id);


--
-- Name: ix_audit_logs_id; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX ix_audit_logs_id ON public.audit_logs USING btree (id);


--
-- Name: ix_notifications_id; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX ix_notifications_id ON public.notifications USING btree (id);


--
-- Name: ix_therapy_plan_items_id; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX ix_therapy_plan_items_id ON public.therapy_plan_items USING btree (id);


--
-- Name: ix_therapy_plans_id; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX ix_therapy_plans_id ON public.therapy_plans USING btree (id);


--
-- Name: ix_therapy_sessions_id; Type: INDEX; Schema: public; Owner: celloxen_user
--

CREATE INDEX ix_therapy_sessions_id ON public.therapy_sessions USING btree (id);


--
-- Name: chatbot_sessions chatbot_sessions_updated_at; Type: TRIGGER; Schema: public; Owner: celloxen_user
--

CREATE TRIGGER chatbot_sessions_updated_at BEFORE UPDATE ON public.chatbot_sessions FOR EACH ROW EXECUTE FUNCTION public.update_chatbot_updated_at();


--
-- Name: iridology_capture_sessions iridology_capture_updated_at; Type: TRIGGER; Schema: public; Owner: celloxen_user
--

CREATE TRIGGER iridology_capture_updated_at BEFORE UPDATE ON public.iridology_capture_sessions FOR EACH ROW EXECUTE FUNCTION public.update_chatbot_updated_at();


--
-- Name: comprehensive_assessments update_comprehensive_assessments_updated_at; Type: TRIGGER; Schema: public; Owner: celloxen_user
--

CREATE TRIGGER update_comprehensive_assessments_updated_at BEFORE UPDATE ON public.comprehensive_assessments FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: chatbot_messages update_session_activity_trigger; Type: TRIGGER; Schema: public; Owner: celloxen_user
--

CREATE TRIGGER update_session_activity_trigger AFTER INSERT ON public.chatbot_messages FOR EACH ROW EXECUTE FUNCTION public.update_session_activity();


--
-- Name: appointments appointments_cancelled_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_cancelled_by_fkey FOREIGN KEY (cancelled_by) REFERENCES public.users(id);


--
-- Name: appointments appointments_clinic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_clinic_id_fkey FOREIGN KEY (clinic_id) REFERENCES public.clinics(id);


--
-- Name: appointments appointments_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: appointments appointments_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(id);


--
-- Name: appointments appointments_practitioner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_practitioner_id_fkey FOREIGN KEY (practitioner_id) REFERENCES public.users(id);


--
-- Name: appointments appointments_therapist_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_therapist_id_fkey FOREIGN KEY (therapist_id) REFERENCES public.users(id);


--
-- Name: assessment_answers assessment_answers_assessment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.assessment_answers
    ADD CONSTRAINT assessment_answers_assessment_id_fkey FOREIGN KEY (assessment_id) REFERENCES public.assessments(id);


--
-- Name: assessment_answers assessment_answers_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.assessment_answers
    ADD CONSTRAINT assessment_answers_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.assessment_questions(id);


--
-- Name: assessments assessments_clinic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.assessments
    ADD CONSTRAINT assessments_clinic_id_fkey FOREIGN KEY (clinic_id) REFERENCES public.clinics(id);


--
-- Name: assessments assessments_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.assessments
    ADD CONSTRAINT assessments_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: assessments assessments_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.assessments
    ADD CONSTRAINT assessments_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(id);


--
-- Name: audit_logs audit_logs_clinic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_clinic_id_fkey FOREIGN KEY (clinic_id) REFERENCES public.clinics(id);


--
-- Name: audit_logs audit_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: chatbot_messages chatbot_messages_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.chatbot_messages
    ADD CONSTRAINT chatbot_messages_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.chatbot_sessions(id) ON DELETE CASCADE;


--
-- Name: chatbot_questions_progress chatbot_questions_progress_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.chatbot_questions_progress
    ADD CONSTRAINT chatbot_questions_progress_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.chatbot_sessions(id) ON DELETE CASCADE;


--
-- Name: chatbot_sessions chatbot_sessions_assessment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.chatbot_sessions
    ADD CONSTRAINT chatbot_sessions_assessment_id_fkey FOREIGN KEY (assessment_id) REFERENCES public.comprehensive_assessments(id);


--
-- Name: chatbot_sessions chatbot_sessions_clinic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.chatbot_sessions
    ADD CONSTRAINT chatbot_sessions_clinic_id_fkey FOREIGN KEY (clinic_id) REFERENCES public.clinics(id);


--
-- Name: chatbot_sessions chatbot_sessions_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.chatbot_sessions
    ADD CONSTRAINT chatbot_sessions_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(id) ON DELETE CASCADE;


--
-- Name: chatbot_sessions chatbot_sessions_practitioner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.chatbot_sessions
    ADD CONSTRAINT chatbot_sessions_practitioner_id_fkey FOREIGN KEY (practitioner_id) REFERENCES public.users(id);


--
-- Name: comprehensive_assessments comprehensive_assessments_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.comprehensive_assessments
    ADD CONSTRAINT comprehensive_assessments_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(id) ON DELETE CASCADE;


--
-- Name: comprehensive_assessments comprehensive_assessments_practitioner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.comprehensive_assessments
    ADD CONSTRAINT comprehensive_assessments_practitioner_id_fkey FOREIGN KEY (practitioner_id) REFERENCES public.users(id);


--
-- Name: contraindication_checks contraindication_checks_assessment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.contraindication_checks
    ADD CONSTRAINT contraindication_checks_assessment_id_fkey FOREIGN KEY (assessment_id) REFERENCES public.comprehensive_assessments(id);


--
-- Name: contraindication_checks contraindication_checks_checked_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.contraindication_checks
    ADD CONSTRAINT contraindication_checks_checked_by_fkey FOREIGN KEY (checked_by) REFERENCES public.users(id);


--
-- Name: contraindication_checks contraindication_checks_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.contraindication_checks
    ADD CONSTRAINT contraindication_checks_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(id);


--
-- Name: domain_followup_responses domain_followup_responses_assessment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.domain_followup_responses
    ADD CONSTRAINT domain_followup_responses_assessment_id_fkey FOREIGN KEY (assessment_id) REFERENCES public.comprehensive_assessments(id);


--
-- Name: domain_followup_responses domain_followup_responses_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.domain_followup_responses
    ADD CONSTRAINT domain_followup_responses_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(id);


--
-- Name: domain_followup_responses domain_followup_responses_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.domain_followup_responses
    ADD CONSTRAINT domain_followup_responses_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.domain_followup_questions(id);


--
-- Name: email_logs email_logs_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_logs
    ADD CONSTRAINT email_logs_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(id);


--
-- Name: iridology_capture_sessions iridology_capture_sessions_assessment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.iridology_capture_sessions
    ADD CONSTRAINT iridology_capture_sessions_assessment_id_fkey FOREIGN KEY (assessment_id) REFERENCES public.comprehensive_assessments(id);


--
-- Name: iridology_capture_sessions iridology_capture_sessions_chatbot_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.iridology_capture_sessions
    ADD CONSTRAINT iridology_capture_sessions_chatbot_session_id_fkey FOREIGN KEY (chatbot_session_id) REFERENCES public.chatbot_sessions(id) ON DELETE CASCADE;


--
-- Name: iridology_findings iridology_findings_assessment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.iridology_findings
    ADD CONSTRAINT iridology_findings_assessment_id_fkey FOREIGN KEY (assessment_id) REFERENCES public.comprehensive_assessments(id) ON DELETE CASCADE;


--
-- Name: patients patients_clinic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.patients
    ADD CONSTRAINT patients_clinic_id_fkey FOREIGN KEY (clinic_id) REFERENCES public.clinics(id);


--
-- Name: therapy_correlations therapy_correlations_assessment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.therapy_correlations
    ADD CONSTRAINT therapy_correlations_assessment_id_fkey FOREIGN KEY (assessment_id) REFERENCES public.comprehensive_assessments(id) ON DELETE CASCADE;


--
-- Name: therapy_plan_items therapy_plan_items_therapy_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.therapy_plan_items
    ADD CONSTRAINT therapy_plan_items_therapy_plan_id_fkey FOREIGN KEY (therapy_plan_id) REFERENCES public.therapy_plans(id);


--
-- Name: therapy_plans therapy_plans_assessment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.therapy_plans
    ADD CONSTRAINT therapy_plans_assessment_id_fkey FOREIGN KEY (assessment_id) REFERENCES public.comprehensive_assessments(id);


--
-- Name: therapy_plans therapy_plans_clinic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.therapy_plans
    ADD CONSTRAINT therapy_plans_clinic_id_fkey FOREIGN KEY (clinic_id) REFERENCES public.clinics(id);


--
-- Name: therapy_plans therapy_plans_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.therapy_plans
    ADD CONSTRAINT therapy_plans_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(id);


--
-- Name: therapy_plans therapy_plans_recommended_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.therapy_plans
    ADD CONSTRAINT therapy_plans_recommended_by_fkey FOREIGN KEY (recommended_by) REFERENCES public.users(id);


--
-- Name: therapy_sessions therapy_sessions_clinic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.therapy_sessions
    ADD CONSTRAINT therapy_sessions_clinic_id_fkey FOREIGN KEY (clinic_id) REFERENCES public.clinics(id);


--
-- Name: therapy_sessions therapy_sessions_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.therapy_sessions
    ADD CONSTRAINT therapy_sessions_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: therapy_sessions therapy_sessions_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.therapy_sessions
    ADD CONSTRAINT therapy_sessions_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(id);


--
-- Name: therapy_sessions therapy_sessions_therapist_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.therapy_sessions
    ADD CONSTRAINT therapy_sessions_therapist_id_fkey FOREIGN KEY (therapist_id) REFERENCES public.users(id);


--
-- Name: therapy_sessions therapy_sessions_therapy_plan_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.therapy_sessions
    ADD CONSTRAINT therapy_sessions_therapy_plan_item_id_fkey FOREIGN KEY (therapy_plan_item_id) REFERENCES public.therapy_plan_items(id);


--
-- Name: users users_clinic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: celloxen_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_clinic_id_fkey FOREIGN KEY (clinic_id) REFERENCES public.clinics(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO celloxen_user;


--
-- Name: TABLE email_logs; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.email_logs TO celloxen_user;


--
-- Name: SEQUENCE email_logs_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE public.email_logs_id_seq TO celloxen_user;


--
-- PostgreSQL database dump complete
--

\unrestrict OVe0vKovjhhZfiW7ThAd4Lxtu6JgMMpg1TAfvvVjGV37uyQZkZRORq4hfiuRG7R

