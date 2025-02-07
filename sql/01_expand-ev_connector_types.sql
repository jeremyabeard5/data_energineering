CREATE TABLE public.ev_connector_types (
    id SERIAL PRIMARY KEY,
    evse_id INTEGER NOT NULL,
    connector_type VARCHAR(255),
    FOREIGN KEY (evse_id) REFERENCES public.evses (id)  -- Adjust the 'id' column to match your primary key column name in 'public.evses'
);

INSERT INTO public.ev_connector_types (evse_id, connector_type)
SELECT id, unnest(string_to_array(regexp_replace(ev_connector_types, '[{}]', '', 'g'), ',')) AS connector_type
FROM public.evses;

SELECT e.*, ect.connector_type
FROM public.evses e
JOIN public.ev_connector_types ect ON e.id = ect.evse_id;