--
-- PostgreSQL database dump
--

\restrict DdftBX07wIsTnO8D5YJlmeRqdliO5pBiJmS43DDbac4Rf6Gq0D7sL5cWgqgbx6X

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
-- Data for Name: clinics; Type: TABLE DATA; Schema: public; Owner: celloxen_user
--

INSERT INTO public.clinics VALUES (1, 'Aberdeen Wellness Centre', 'info@aberdeenwellness.co.uk', '01224 123456', '123 Union Street', 'Aberdeen', 'AB10 1AA', 'United Kingdom', 'active', '2025-11-08 20:07:26.625225');


--
-- Data for Name: patients; Type: TABLE DATA; Schema: public; Owner: celloxen_user
--

INSERT INTO public.patients VALUES (1, 'CLX-ABD-00001', 1, 'John', 'Smith', 'john.smith@email.com', '07700 123456', '1975-06-15', 'active', true, '2025-11-08 20:07:26.629008', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO public.patients VALUES (2, 'CLX-ABD-00002', 1, 'Hafsa', 'Rguib', 'hafsarguib@yahoo.fr', '07393960664', '1999-09-02', 'active', true, '2025-11-08 22:08:15.39508', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO public.patients VALUES (4, 'CLX-ABD-00003', 1, 'Sam', 'Naqvi', 'info@naqvii.com', '039393837773', '1950-02-22', 'active', true, '2025-11-08 22:31:26.770509', '123 High Street , Manchester, M1 2LU', 'John Raggi', '0800655999', 'blood pressure', 'A|b6555', 'NONE', '', 'Anxiety');


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: celloxen_user
--

INSERT INTO public.users VALUES (1, 'admin@celloxen.com', '$2b$12$LQv3c1yqBwfNp1cT8MEVUOGdlEzGYKj1OZF7VJcK8GGlEkJyPtf4.', 'Celloxen Admin', 'super_admin', NULL, 'active', '2025-11-08 20:07:26.626769');
INSERT INTO public.users VALUES (2, 'staff@aberdeenwellness.co.uk', '$2b$12$LQv3c1yqBwfNp1cT8MEVUOGdlEzGYKj1OZF7VJcK8GGlEkJyPtf4.', 'Aberdeen Clinic Staff', 'clinic_user', 1, 'active', '2025-11-08 20:07:26.627947');


--
-- Name: clinics_id_seq; Type: SEQUENCE SET; Schema: public; Owner: celloxen_user
--

SELECT pg_catalog.setval('public.clinics_id_seq', 1, true);


--
-- Name: patients_id_seq; Type: SEQUENCE SET; Schema: public; Owner: celloxen_user
--

SELECT pg_catalog.setval('public.patients_id_seq', 4, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: celloxen_user
--

SELECT pg_catalog.setval('public.users_id_seq', 2, true);


--
-- PostgreSQL database dump complete
--

\unrestrict DdftBX07wIsTnO8D5YJlmeRqdliO5pBiJmS43DDbac4Rf6Gq0D7sL5cWgqgbx6X

