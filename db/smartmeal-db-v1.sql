--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4
-- Dumped by pg_dump version 17.4

-- Started on 2025-03-24 13:34:32

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 220 (class 1259 OID 16400)
-- Name: inventory; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.inventory (
    inventory_id integer NOT NULL,
    user_id integer,
    ustensils jsonb[],
    grocery jsonb[],
    fresh_produce jsonb[]
);


ALTER TABLE public.inventory OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16399)
-- Name: inventory_inventory_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.inventory_inventory_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.inventory_inventory_id_seq OWNER TO postgres;

--
-- TOC entry 4919 (class 0 OID 0)
-- Dependencies: 219
-- Name: inventory_inventory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.inventory_inventory_id_seq OWNED BY public.inventory.inventory_id;


--
-- TOC entry 222 (class 1259 OID 16414)
-- Name: preferences; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.preferences (
    preference_id integer NOT NULL,
    user_id integer,
    allergy jsonb,
    diet text,
    goal text,
    new integer,
    number_of_meals integer,
    grocery_day text,
    language text,
    CONSTRAINT preferences_new_check CHECK (((new >= 1) AND (new <= 5)))
);


ALTER TABLE public.preferences OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16413)
-- Name: preferences_preference_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.preferences_preference_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.preferences_preference_id_seq OWNER TO postgres;

--
-- TOC entry 4920 (class 0 OID 0)
-- Dependencies: 221
-- Name: preferences_preference_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.preferences_preference_id_seq OWNED BY public.preferences.preference_id;


--
-- TOC entry 228 (class 1259 OID 16457)
-- Name: recipes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.recipes (
    recipe_id integer NOT NULL,
    recipe_name text NOT NULL,
    recipe_ingredients jsonb,
    recipe_instructions jsonb,
    recipe_preparation_time integer,
    recipe_ustensils_required jsonb,
    recipe_nutritional_value jsonb
);


ALTER TABLE public.recipes OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 16456)
-- Name: recipes_recipe_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.recipes_recipe_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.recipes_recipe_id_seq OWNER TO postgres;

--
-- TOC entry 4921 (class 0 OID 0)
-- Dependencies: 227
-- Name: recipes_recipe_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.recipes_recipe_id_seq OWNED BY public.recipes.recipe_id;


--
-- TOC entry 224 (class 1259 OID 16429)
-- Name: shopping_list; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.shopping_list (
    shoppinglist_id integer NOT NULL,
    user_id integer,
    grocery jsonb,
    fresh_produce jsonb,
    fruit_and_vegetables jsonb
);


ALTER TABLE public.shopping_list OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16428)
-- Name: shopping_list_shoppinglist_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.shopping_list_shoppinglist_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.shopping_list_shoppinglist_id_seq OWNER TO postgres;

--
-- TOC entry 4922 (class 0 OID 0)
-- Dependencies: 223
-- Name: shopping_list_shoppinglist_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.shopping_list_shoppinglist_id_seq OWNED BY public.shopping_list.shoppinglist_id;


--
-- TOC entry 230 (class 1259 OID 16483)
-- Name: user_recipes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_recipes (
    user_recipes_id integer NOT NULL,
    user_id integer NOT NULL,
    recipe_id integer NOT NULL,
    personalisation jsonb
);


ALTER TABLE public.user_recipes OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 16482)
-- Name: user_recipes_user_recipes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_recipes_user_recipes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_recipes_user_recipes_id_seq OWNER TO postgres;

--
-- TOC entry 4923 (class 0 OID 0)
-- Dependencies: 229
-- Name: user_recipes_user_recipes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_recipes_user_recipes_id_seq OWNED BY public.user_recipes.user_recipes_id;


--
-- TOC entry 218 (class 1259 OID 16389)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    user_name text NOT NULL,
    user_surname text NOT NULL,
    user_email text NOT NULL,
    user_password text NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 16388)
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_user_id_seq OWNER TO postgres;

--
-- TOC entry 4924 (class 0 OID 0)
-- Dependencies: 217
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- TOC entry 226 (class 1259 OID 16443)
-- Name: weeks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.weeks (
    week_id integer NOT NULL,
    user_id integer,
    lundi jsonb[],
    mardi jsonb[],
    mercredi jsonb[],
    jeudi jsonb[],
    vendredi jsonb[],
    samedi jsonb[],
    dimanche jsonb[]
);


ALTER TABLE public.weeks OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 16442)
-- Name: weeks_week_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.weeks_week_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.weeks_week_id_seq OWNER TO postgres;

--
-- TOC entry 4925 (class 0 OID 0)
-- Dependencies: 225
-- Name: weeks_week_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.weeks_week_id_seq OWNED BY public.weeks.week_id;


--
-- TOC entry 4726 (class 2604 OID 16403)
-- Name: inventory inventory_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory ALTER COLUMN inventory_id SET DEFAULT nextval('public.inventory_inventory_id_seq'::regclass);


--
-- TOC entry 4727 (class 2604 OID 16417)
-- Name: preferences preference_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.preferences ALTER COLUMN preference_id SET DEFAULT nextval('public.preferences_preference_id_seq'::regclass);


--
-- TOC entry 4730 (class 2604 OID 16460)
-- Name: recipes recipe_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recipes ALTER COLUMN recipe_id SET DEFAULT nextval('public.recipes_recipe_id_seq'::regclass);


--
-- TOC entry 4728 (class 2604 OID 16432)
-- Name: shopping_list shoppinglist_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shopping_list ALTER COLUMN shoppinglist_id SET DEFAULT nextval('public.shopping_list_shoppinglist_id_seq'::regclass);


--
-- TOC entry 4731 (class 2604 OID 16486)
-- Name: user_recipes user_recipes_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_recipes ALTER COLUMN user_recipes_id SET DEFAULT nextval('public.user_recipes_user_recipes_id_seq'::regclass);


--
-- TOC entry 4725 (class 2604 OID 16392)
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- TOC entry 4729 (class 2604 OID 16446)
-- Name: weeks week_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.weeks ALTER COLUMN week_id SET DEFAULT nextval('public.weeks_week_id_seq'::regclass);


--
-- TOC entry 4903 (class 0 OID 16400)
-- Dependencies: 220
-- Data for Name: inventory; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.inventory (inventory_id, user_id, ustensils, grocery, fresh_produce) VALUES (1, 1, '{"{\"name\": \"spatula\", \"quantity\": 1}"}', '{"{\"name\": \"rice\", \"quantity\": 2, \"type_quantity\": \"kg\"}"}', '{"{\"name\": \"carrot\", \"quantity\": 3}"}');
INSERT INTO public.inventory (inventory_id, user_id, ustensils, grocery, fresh_produce) VALUES (2, 2, '{"{\"name\": \"knife\", \"quantity\": 1}"}', '{"{\"name\": \"flour\", \"quantity\": 1, \"type_quantity\": \"kg\"}"}', '{"{\"name\": \"apple\", \"quantity\": 4}"}');
INSERT INTO public.inventory (inventory_id, user_id, ustensils, grocery, fresh_produce) VALUES (3, 3, '{"{\"name\": \"pan\", \"quantity\": 1}"}', '{"{\"name\": \"sugar\", \"quantity\": 1, \"type_quantity\": \"kg\"}"}', '{"{\"name\": \"banana\", \"quantity\": 6}"}');
INSERT INTO public.inventory (inventory_id, user_id, ustensils, grocery, fresh_produce) VALUES (4, 4, '{"{\"name\": \"bowl\", \"quantity\": 2}"}', '{"{\"name\": \"salt\", \"quantity\": 1, \"type_quantity\": \"g\"}"}', '{"{\"name\": \"tomato\", \"quantity\": 5}"}');
INSERT INTO public.inventory (inventory_id, user_id, ustensils, grocery, fresh_produce) VALUES (5, 5, '{"{\"name\": \"whisk\", \"quantity\": 1}"}', '{"{\"name\": \"pepper\", \"quantity\": 1, \"type_quantity\": \"g\"}"}', '{"{\"name\": \"cucumber\", \"quantity\": 2}"}');


--
-- TOC entry 4905 (class 0 OID 16414)
-- Dependencies: 222
-- Data for Name: preferences; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.preferences (preference_id, user_id, allergy, diet, goal, new, number_of_meals, grocery_day, language) VALUES (1, 1, '{"allergy1": "peanut"}', 'vegan', 'lose weight', 3, 3, 'Monday', 'English');
INSERT INTO public.preferences (preference_id, user_id, allergy, diet, goal, new, number_of_meals, grocery_day, language) VALUES (2, 2, '{"allergy1": "gluten"}', 'vegetarian', 'gain muscle', 4, 4, 'Wednesday', 'French');
INSERT INTO public.preferences (preference_id, user_id, allergy, diet, goal, new, number_of_meals, grocery_day, language) VALUES (3, 3, '{"allergy1": "lactose"}', 'keto', 'maintain weight', 5, 3, 'Friday', 'Spanish');
INSERT INTO public.preferences (preference_id, user_id, allergy, diet, goal, new, number_of_meals, grocery_day, language) VALUES (4, 4, '{"allergy1": "seafood"}', 'paleo', 'increase stamina', 2, 5, 'Saturday', 'German');
INSERT INTO public.preferences (preference_id, user_id, allergy, diet, goal, new, number_of_meals, grocery_day, language) VALUES (5, 5, '{"allergy1": "egg"}', 'omnivore', 'better health', 1, 3, 'Sunday', 'Italian');


--
-- TOC entry 4911 (class 0 OID 16457)
-- Dependencies: 228
-- Data for Name: recipes; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.recipes (recipe_id, recipe_name, recipe_ingredients, recipe_instructions, recipe_preparation_time, recipe_ustensils_required, recipe_nutritional_value) VALUES (1, 'Spaghetti Carbonara', '{"egg": 2, "bacon": 100, "spaghetti": 200}', '{"step1": "Boil pasta", "step2": "Cook bacon", "step3": "Mix together"}', 20, '{"pan": 1, "pot": 1}', '{"protein": 20, "calories": 500}');
INSERT INTO public.recipes (recipe_id, recipe_name, recipe_ingredients, recipe_instructions, recipe_preparation_time, recipe_ustensils_required, recipe_nutritional_value) VALUES (2, 'Caesar Salad', '{"chicken": 100, "lettuce": 1, "croutons": 50}', '{"step1": "Chop lettuce", "step2": "Cook chicken", "step3": "Mix together"}', 15, '{"bowl": 1, "knife": 1}', '{"protein": 25, "calories": 300}');
INSERT INTO public.recipes (recipe_id, recipe_name, recipe_ingredients, recipe_instructions, recipe_preparation_time, recipe_ustensils_required, recipe_nutritional_value) VALUES (3, 'Grilled Salmon', '{"lemon": 1, "garlic": 1, "salmon": 200}', '{"step1": "Season salmon", "step2": "Grill salmon"}', 25, '{"grill": 1, "tongs": 1}', '{"protein": 35, "calories": 450}');
INSERT INTO public.recipes (recipe_id, recipe_name, recipe_ingredients, recipe_instructions, recipe_preparation_time, recipe_ustensils_required, recipe_nutritional_value) VALUES (4, 'Vegetable Stir Fry', '{"tofu": 100, "carrot": 1, "broccoli": 1}', '{"step1": "Chop veggies", "step2": "Stir fry"}', 20, '{"wok": 1, "spatula": 1}', '{"protein": 15, "calories": 400}');
INSERT INTO public.recipes (recipe_id, recipe_name, recipe_ingredients, recipe_instructions, recipe_preparation_time, recipe_ustensils_required, recipe_nutritional_value) VALUES (5, 'Chicken Curry', '{"chicken": 200, "coconut milk": 1, "curry powder": 10}', '{"step1": "Cook chicken", "step2": "Add curry sauce"}', 30, '{"pan": 1, "knife": 1}', '{"protein": 40, "calories": 550}');


--
-- TOC entry 4907 (class 0 OID 16429)
-- Dependencies: 224
-- Data for Name: shopping_list; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.shopping_list (shoppinglist_id, user_id, grocery, fresh_produce, fruit_and_vegetables) VALUES (1, 1, '{"rice": 2}', '{"carrot": 3}', '{"apple": 5}');
INSERT INTO public.shopping_list (shoppinglist_id, user_id, grocery, fresh_produce, fruit_and_vegetables) VALUES (2, 2, '{"flour": 1}', '{"tomato": 2}', '{"banana": 6}');
INSERT INTO public.shopping_list (shoppinglist_id, user_id, grocery, fresh_produce, fruit_and_vegetables) VALUES (3, 3, '{"sugar": 1}', '{"lettuce": 1}', '{"grape": 3}');
INSERT INTO public.shopping_list (shoppinglist_id, user_id, grocery, fresh_produce, fruit_and_vegetables) VALUES (4, 4, '{"salt": 1}', '{"onion": 4}', '{"pear": 2}');
INSERT INTO public.shopping_list (shoppinglist_id, user_id, grocery, fresh_produce, fruit_and_vegetables) VALUES (5, 5, '{"pepper": 1}', '{"potato": 5}', '{"orange": 4}');


--
-- TOC entry 4913 (class 0 OID 16483)
-- Dependencies: 230
-- Data for Name: user_recipes; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.user_recipes (user_recipes_id, user_id, recipe_id, personalisation) VALUES (6, 1, 1, '{"spiciness": "mild", "extra_ingredients": ["cheese", "basil"]}');
INSERT INTO public.user_recipes (user_recipes_id, user_id, recipe_id, personalisation) VALUES (7, 2, 2, '{"exclude": ["garlic"], "spiciness": "hot"}');
INSERT INTO public.user_recipes (user_recipes_id, user_id, recipe_id, personalisation) VALUES (8, 3, 3, '{"cooking_time": "30min", "portion_size": "large"}');
INSERT INTO public.user_recipes (user_recipes_id, user_id, recipe_id, personalisation) VALUES (9, 1, 4, '{"notes": "Less salt", "extra_ingredients": ["mushrooms"]}');
INSERT INTO public.user_recipes (user_recipes_id, user_id, recipe_id, personalisation) VALUES (10, 2, 5, '{"diet": "vegan", "substitutes": {"milk": "almond milk"}}');


--
-- TOC entry 4901 (class 0 OID 16389)
-- Dependencies: 218
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.users (user_id, user_name, user_surname, user_email, user_password) VALUES (1, 'Alice', 'Dupont', 'alice.dupont@email.com', 'hashed_password1');
INSERT INTO public.users (user_id, user_name, user_surname, user_email, user_password) VALUES (2, 'Bob', 'Martin', 'bob.martin@email.com', 'hashed_password2');
INSERT INTO public.users (user_id, user_name, user_surname, user_email, user_password) VALUES (3, 'Charlie', 'Durand', 'charlie.durand@email.com', 'hashed_password3');
INSERT INTO public.users (user_id, user_name, user_surname, user_email, user_password) VALUES (4, 'David', 'Lemoine', 'david.lemoine@email.com', 'hashed_password4');
INSERT INTO public.users (user_id, user_name, user_surname, user_email, user_password) VALUES (5, 'Emma', 'Bernard', 'emma.bernard@email.com', 'hashed_password5');


--
-- TOC entry 4909 (class 0 OID 16443)
-- Dependencies: 226
-- Data for Name: weeks; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.weeks (week_id, user_id, lundi, mardi, mercredi, jeudi, vendredi, samedi, dimanche) VALUES (1, 1, '{"{\"meal1\": \"pasta\"}"}', '{"{\"meal1\": \"salad\"}"}', '{"{\"meal1\": \"rice\"}"}', '{"{\"meal1\": \"fish\"}"}', '{"{\"meal1\": \"soup\"}"}', '{"{\"meal1\": \"burger\"}"}', '{"{\"meal1\": \"pizza\"}"}');
INSERT INTO public.weeks (week_id, user_id, lundi, mardi, mercredi, jeudi, vendredi, samedi, dimanche) VALUES (2, 2, '{"{\"meal1\": \"chicken\"}"}', '{"{\"meal1\": \"tofu\"}"}', '{"{\"meal1\": \"lentils\"}"}', '{"{\"meal1\": \"pork\"}"}', '{"{\"meal1\": \"sushi\"}"}', '{"{\"meal1\": \"tacos\"}"}', '{"{\"meal1\": \"steak\"}"}');
INSERT INTO public.weeks (week_id, user_id, lundi, mardi, mercredi, jeudi, vendredi, samedi, dimanche) VALUES (3, 3, '{"{\"meal1\": \"omelette\"}"}', '{"{\"meal1\": \"pasta\"}"}', '{"{\"meal1\": \"burrito\"}"}', '{"{\"meal1\": \"quinoa\"}"}', '{"{\"meal1\": \"salmon\"}"}', '{"{\"meal1\": \"pancakes\"}"}', '{"{\"meal1\": \"soup\"}"}');
INSERT INTO public.weeks (week_id, user_id, lundi, mardi, mercredi, jeudi, vendredi, samedi, dimanche) VALUES (4, 4, '{"{\"meal1\": \"stir fry\"}"}', '{"{\"meal1\": \"falafel\"}"}', '{"{\"meal1\": \"pizza\"}"}', '{"{\"meal1\": \"pasta\"}"}', '{"{\"meal1\": \"lasagna\"}"}', '{"{\"meal1\": \"soup\"}"}', '{"{\"meal1\": \"stew\"}"}');
INSERT INTO public.weeks (week_id, user_id, lundi, mardi, mercredi, jeudi, vendredi, samedi, dimanche) VALUES (5, 5, '{"{\"meal1\": \"ramen\"}"}', '{"{\"meal1\": \"sandwich\"}"}', '{"{\"meal1\": \"wrap\"}"}', '{"{\"meal1\": \"chili\"}"}', '{"{\"meal1\": \"grilled cheese\"}"}', '{"{\"meal1\": \"sushi\"}"}', '{"{\"meal1\": \"pasta\"}"}');


--
-- TOC entry 4926 (class 0 OID 0)
-- Dependencies: 219
-- Name: inventory_inventory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.inventory_inventory_id_seq', 5, true);


--
-- TOC entry 4927 (class 0 OID 0)
-- Dependencies: 221
-- Name: preferences_preference_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.preferences_preference_id_seq', 5, true);


--
-- TOC entry 4928 (class 0 OID 0)
-- Dependencies: 227
-- Name: recipes_recipe_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.recipes_recipe_id_seq', 5, true);


--
-- TOC entry 4929 (class 0 OID 0)
-- Dependencies: 223
-- Name: shopping_list_shoppinglist_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.shopping_list_shoppinglist_id_seq', 5, true);


--
-- TOC entry 4930 (class 0 OID 0)
-- Dependencies: 229
-- Name: user_recipes_user_recipes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_recipes_user_recipes_id_seq', 10, true);


--
-- TOC entry 4931 (class 0 OID 0)
-- Dependencies: 217
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_user_id_seq', 5, true);


--
-- TOC entry 4932 (class 0 OID 0)
-- Dependencies: 225
-- Name: weeks_week_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.weeks_week_id_seq', 5, true);


--
-- TOC entry 4738 (class 2606 OID 16407)
-- Name: inventory inventory_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_pkey PRIMARY KEY (inventory_id);


--
-- TOC entry 4740 (class 2606 OID 16422)
-- Name: preferences preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.preferences
    ADD CONSTRAINT preferences_pkey PRIMARY KEY (preference_id);


--
-- TOC entry 4746 (class 2606 OID 16464)
-- Name: recipes recipes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recipes
    ADD CONSTRAINT recipes_pkey PRIMARY KEY (recipe_id);


--
-- TOC entry 4742 (class 2606 OID 16436)
-- Name: shopping_list shopping_list_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shopping_list
    ADD CONSTRAINT shopping_list_pkey PRIMARY KEY (shoppinglist_id);


--
-- TOC entry 4748 (class 2606 OID 16490)
-- Name: user_recipes user_recipes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_recipes
    ADD CONSTRAINT user_recipes_pkey PRIMARY KEY (user_recipes_id);


--
-- TOC entry 4734 (class 2606 OID 16396)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- TOC entry 4736 (class 2606 OID 16398)
-- Name: users users_user_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_user_email_key UNIQUE (user_email);


--
-- TOC entry 4744 (class 2606 OID 16450)
-- Name: weeks weeks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.weeks
    ADD CONSTRAINT weeks_pkey PRIMARY KEY (week_id);


--
-- TOC entry 4753 (class 2606 OID 16496)
-- Name: user_recipes fk_user_recipes_recipe; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_recipes
    ADD CONSTRAINT fk_user_recipes_recipe FOREIGN KEY (recipe_id) REFERENCES public.recipes(recipe_id) ON DELETE CASCADE;


--
-- TOC entry 4754 (class 2606 OID 16491)
-- Name: user_recipes fk_user_recipes_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_recipes
    ADD CONSTRAINT fk_user_recipes_user FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- TOC entry 4749 (class 2606 OID 16408)
-- Name: inventory inventory_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- TOC entry 4750 (class 2606 OID 16423)
-- Name: preferences preferences_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.preferences
    ADD CONSTRAINT preferences_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- TOC entry 4751 (class 2606 OID 16437)
-- Name: shopping_list shopping_list_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shopping_list
    ADD CONSTRAINT shopping_list_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- TOC entry 4752 (class 2606 OID 16451)
-- Name: weeks weeks_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.weeks
    ADD CONSTRAINT weeks_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


-- Completed on 2025-03-24 13:34:32

--
-- PostgreSQL database dump complete
--

