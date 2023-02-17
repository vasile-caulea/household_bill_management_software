describe contracts;
describe invoices;
describe persons;
describe services_descriptions;
describe providers_services;
describe providers;
describe services;
describe tariffs_types;


------- TESTARE CONSTRANGERI PENTRU TABELA PERSONS -------
-- testare constrangere nume persoana carctere invalide
INSERT INTO persons ( full_name, phone_no, address, email )
VALUES ('Popa Lucian21', '0232882860', 'Strada Soveja nr. 110, Iasi', 'popa.lucian21@mail.com');

-- testare constrangere nume persoana dimensiune camp
INSERT INTO persons ( full_name, phone_no, address, email )
VALUES ('P', '0232882860', 'Strada Soveja nr. 110, Iasi', 'popa.lucian21@mail.com');

-- testare constrangere numar de telefon unic
INSERT INTO persons ( full_name, phone_no, address, email ) 
VALUES ( 'Popescu Ion', '0232882860', 'Strada Soveja nr. 110, Iasi', 'popescu-ion@mgs.org' );

-- testare constrangere format numar de telefon
INSERT INTO persons ( full_name, phone_no, address, email ) 
VALUES ( 'Popescu Ion', '023,288-2860', 'Strada Soveja nr. 110, Iasi', 'popescu-ion@mgs.org' );

-- testare constrangere lungime camp adresa domiciliu
INSERT INTO persons ( full_name, phone_no, address, email ) 
VALUES ( 'Popescu Ion', '0789900099', 'a', 'popescu-ion@mgs.org' );

-- testare constrangere format adresa email 
INSERT INTO persons ( full_name, phone_no, address, email ) 
VALUES ( 'Popescu Ion', '0789900099', 'Strada Soveja nr. 110, Iasi', 'popescu-ion.mgs.org' );

-- testare constrangere unicitate adresa email
INSERT INTO persons ( full_name, phone_no, address, email ) 
VALUES ( 'Popescu Ion', '0789900099', 'Strada Soveja nr. 110, Iasi', 'carina.pavel@outlook.com' );


------- TESTARE CONSTRANGERI PENTRU TABELA TARIFFS_TYPES -------
-- testare constrangere lungime camp name
INSERT INTO tariffs_types ( name ) VALUES ( 'k' );

-- testare constrangere unicitate nume
INSERT INTO tariffs_types ( name ) VALUES ( 'RON/kWh' );


------- TESTARE CONSTRANGERI PENTRU TABELA SERVICES_DESCRIPTIONS -------
-- testare constrangere lungime descriere serviciu
INSERT INTO services_descriptions VALUES ( 1, 'd' );


------- TESTARE CONSTRANGERI PENTRU TABELA SERVICES -------
-- testare constrangere camp name unic
INSERT INTO services ( name, id_tariff_type ) VALUES ( 'Electricitate', 1 );

-- testare constrangere lungime camp name
INSERT INTO services ( name, id_tariff_type ) VALUES ( 'a', 1 );

------- TESTARE CONSTRANGERI PENTRU TABELA PROVIDERS -------
-- testare constrangere camp name unic
INSERT INTO providers ( name ) VALUES ( 'E.ON' );

-- testare constrangere lungime camp name
INSERT INTO providers ( name ) VALUES ( 'e' );

------- TESTARE CONSTRANGERI PENTRU TABELA PROVIDERS_SERVICES -------
-- testare constrangere unicitate producator, serviciu oferit
INSERT INTO providers_services ( id_provider, id_service, price)
VALUES ( 1, 1, 4.67);

-- testare constrangere camp price
INSERT INTO providers_services ( id_provider, id_service, price)
VALUES ( 1, 4, 0);

------- TESTARE CONSTRANGERI PENTRU TABELA CONTRACTS -------
-- testare constrangere camp start_date valid
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(10, 17, to_date('06/02/2023', 'dd/mm/yyyy'));

-- testare constrangere camp end_date valid
INSERT INTO contracts(id_person, id_ps, start_date, end_date) 
VALUES(10, 17, to_date('06/02/2020', 'dd/mm/yyyy'), to_date('05/01/2020', 'dd/mm/yyyy'));

------- TESTARE CONSTRANGERI PENTRU TABELA INVOICES -------
-- testare constrangere camp receipt_date valid
INSERT INTO invoices(id_contract, receipt_date, due_date, consumption)
VALUES(1, to_date('06/02/2023', 'dd/mm/yyyy'), sysdate + 14, 1);

-- testare constrangere camp due_date valid
INSERT INTO invoices(id_contract, receipt_date, due_date, consumption)
VALUES(1, sysdate, sysdate - 14, 1);

-- testare constrangere contract neincheiat
INSERT INTO invoices(id_contract, receipt_date, due_date, consumption)
VALUES(33, sysdate, sysdate + 14, 10);

------- TESTARE CONSTRANGERI NONTRANSFERABILITATE  -------
-- testare nontransferabilitate pentru persoana unui contract
UPDATE contracts SET id_person = 2 WHERE id_contract = 1;

-- testare nontransferabilitate pentru furnizorul si serviciile contractului
UPDATE contracts SET id_ps = 2 WHERE id_contract = 1;

-- testare nontransferabilitate pentru contractul pe baza caruia s-a generat factura
UPDATE invoices SET id_contract = 2 WHERE id_invoice = 1;

-- testare nontransferabilitate pentru furnizorul unei inregistrari in tabela providers_services
UPDATE providers_services SET id_provider = 2 WHERE id_ps = 1;

-- testare nontransferabilitate pentru serviciul unei inregistrari in tabela providers_services
UPDATE providers_services SET id_service = 2 WHERE id_ps = 1;


------- TESTARE OPERATII VIZUALIZARE  -------

-- afisare date persoane pentru care nu exista adresa de e-mail
SELECT * FROM persons WHERE email is NULL;

-- afisare contracte neincheiate pentru persoana 'Popa Lucian'
SELECT * FROM contracts 
WHERE end_date is NULL 
AND id_person = (SELECT id_person FROM persons 
WHERE UPPER(full_name) = 'POPA LUCIAN');

-- afisare denumire si detaliile serviciilor, numele furnizorului pentru contractele persoanei 'Popa Lucian'
SELECT pr.name "Provider name", s.name "Service name", sd.description "Service description"
FROM contracts c, providers_services ps, providers pr, services s,
services_descriptions sd, persons p
WHERE UPPER(p.full_name) = 'POPA LUCIAN' 
AND c.id_person = p.id_person 
AND c.id_ps = ps.id_ps 
AND ps.id_service  = s.id_service 
AND ps.id_provider = pr.id_provider
AND sd.id_service(+) = s.id_service;

-- afisare contracte incheiate pentru toate persoanele
SELECT p.full_name || ' are un conctract incheiat cu furnizorul ' 
|| pr.name || ' pentru serviciile ' || s.name 
|| ', pentru care pretul este ' || ps.price || ' ' || tt.name
AS "Contracte incheiate"
FROM contracts c, providers_services ps, providers pr, services s, persons p, tariffs_types tt
WHERE c.id_person = p.id_person
AND c.id_ps = ps.id_ps 
AND ps.id_service  = s.id_service 
AND s.id_tariff_type = tt.id_tariff_type
AND ps.id_provider = pr.id_provider;

-- afisare facturi pentru toate persoanele
SELECT p.full_name || ' are o factura primit? la data ' 
|| TO_CHAR(i.receipt_date, 'DD.MM.YYYY') || ' cu un total de ' 
|| i.payment || ' RON, cu data scadenta ' || TO_CHAR(i.due_date, 'DD.MM.YYYY')
AS "Facturi primite"
FROM contracts c, providers_services ps, providers pr, services s, persons p, 
tariffs_types tt, invoices i
WHERE i.id_contract = c.id_contract
AND c.id_person = p.id_person
AND c.id_ps = ps.id_ps 
AND ps.id_service  = s.id_service 
AND s.id_tariff_type = tt.id_tariff_type
AND ps.id_provider = pr.id_provider;



