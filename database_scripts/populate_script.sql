 -- populare tabela tariff_types
INSERT INTO tariffs_types ( name ) VALUES ( 'RON/kWh' );
INSERT INTO tariffs_types ( name ) VALUES ( 'RON/luna' );
INSERT INTO tariffs_types ( name ) VALUES ( 'RON/mc' );

 -- populare tabela services
INSERT INTO services ( name, id_tariff_type) VALUES ( 'Electricitate',  1);
INSERT INTO services ( name, id_tariff_type) VALUES ( 'Gaz', 1);
INSERT INTO services ( name, id_tariff_type) VALUES ( 'Electricitate, Gaz', 1);
INSERT INTO services ( name, id_tariff_type) VALUES ( 'TV', 2);
INSERT INTO services ( name, id_tariff_type) VALUES ( 'Mobil', 2);
INSERT INTO services ( name, id_tariff_type) VALUES ( 'Internet', 2);
INSERT INTO services ( name, id_tariff_type) VALUES ( 'TV, Mobil', 2);
INSERT INTO services ( name, id_tariff_type) VALUES ( 'TV, Internet', 2);
INSERT INTO services ( name, id_tariff_type) VALUES ( 'Mobil, Internet', 2);
INSERT INTO services ( name, id_tariff_type) VALUES ( 'TV, Mobil, Internet', 2);
INSERT INTO services ( name, id_tariff_type) VALUES ( 'Apa', 3);
INSERT INTO services ( name, id_tariff_type) VALUES ( 'Canalizare', 3);
INSERT INTO services ( name, id_tariff_type) VALUES ( 'Apa, Canalizare', 3);
INSERT INTO services ( name, id_tariff_type) VALUES ( 'Salubrizare', 2);

 -- populare tabela services_descriptions
INSERT INTO services_descriptions
VALUES(11, 'Captarea si pomparea cantitatilor de apa necesare a fi tratate si furnizate.');
INSERT INTO services_descriptions
VALUES(12, 'Evacuarea integrala a apelor uzate menajere.');
INSERT INTO services_descriptions
VALUES(13, 'Captarea, tratarea, distributia apei si colectarea apelor uzate');
INSERT INTO services_descriptions
VALUES(14, 'Colectarea si transportarea deseurilor menajere.');

    -- populare tabela providers
INSERT INTO providers (name) VALUES ('E.ON');
INSERT INTO providers (name) VALUES ('Digi');
INSERT INTO providers (name) VALUES ('Telekom');
INSERT INTO providers (name) VALUES ('Orange');
INSERT INTO providers (name) VALUES ('Vodafone');
INSERT INTO providers (name) VALUES ('Apavital');
INSERT INTO providers (name) VALUES ('Salubris');

 -- populare tabela persons
INSERT INTO persons ( full_name, phone_no, address, email ) 
VALUES ('Popa Lucian', '0232882860', 'Strada Soveja nr. 110, Iasi', '');
INSERT INTO persons ( full_name, phone_no, address, email ) 
VALUES ('Diaconescu Stefan', '0751224444', 'Strada Macarenco nr. 7, Iasi', 'diaconescu.stefan@msn.com');
INSERT INTO persons ( full_name, phone_no, address, email ) 
VALUES ('Sonda Elena', '0370447250', 'Strada Sfintii Constantin si Elena nr. 39, Iasi', '');
INSERT INTO persons ( full_name, phone_no, address, email ) 
VALUES ('Pavel Carina', '0774026776', 'Strada Fotino Dionisie nr. 2, Iasi', 'carina.pavel@outlook.com');
INSERT INTO persons ( full_name, phone_no, address, email ) 
VALUES ('Dinu Sebastian', '0774617740', 'Prelungire Cosuna, 3, Iasi', 'dinu.sebastian@outlook.com');
INSERT INTO persons ( full_name, phone_no, address, email ) 
VALUES ('Negoita Vicentiu', '0713054066', 'Strada Codrului nr. 1, Iasi', 'vicentiu_negoita@msn.com');
INSERT INTO persons ( full_name, phone_no, address, email ) 
VALUES ('Catalin Vlad', '0717676249', 'Strada 9 Mai, 1, Iasi', '');
INSERT INTO persons ( full_name, phone_no, address, email ) 
VALUES ('Craciun Livia', '0369558787', 'Strada Domnita Ruxandra nr. 1, Iasi', 'craciun.livia@aol.com');
INSERT INTO persons ( full_name, phone_no, address, email ) 
VALUES ('Diaconu Catalin', '0722392979', 'Strada 9 Mai nr. 25, Iasi', 'catalin.diaconu@outlook.com');
INSERT INTO persons ( full_name, phone_no, address, email ) 
VALUES ('Vilculescu Carmen', '0763068525', 'Strada Coacazelor, 16,Iasi', 'vilculescu.carmen@att.net');
INSERT INTO persons ( full_name, phone_no, address, email ) 
VALUES ('Birsan Livia', '0214575731', 'Strada Iasilor nr. 21, Iasi', 'livia_birsan@outlook.com');
INSERT INTO persons ( full_name, phone_no, address, email ) 
VALUES ('Gherghe Otilia', '0762382525', 'Strada Gilortului, 16, Iasi', 'gherghe.otilia@msn.com');
INSERT INTO persons ( full_name, phone_no, address, email ) 
VALUES ('Ilies Madalina', '0213939244', 'Strada Varfului, 32, Iasi', 'ilies.madalina@hotmail.com');
INSERT INTO persons ( full_name, phone_no, address, email ) 
VALUES ('Dobrica Stefania', '0747977400', 'Strada Elena Cuza Doamna, 26, Iasi', 'stefania.dobrica@aol.com');
INSERT INTO persons ( full_name, phone_no, address, email ) 
VALUES ('Gherghe Victoria', '0350813557', 'Strada Alunului nr. 2-32, 27, Iasi', 'victoria_gherghe@aol.com');
INSERT INTO persons ( full_name, phone_no, address, email ) 
VALUES ('Negoita Lucian', '0791300837', 'Strada Dorna nr. 34, Iasi', 'lucian_negoita@hotmail.com');

 -- populare tabela providers_services
INSERT INTO providers_services(id_provider, id_service, price) VALUES(1, 1, 4.67);
INSERT INTO providers_services(id_provider, id_service, price) VALUES(1, 2, 1.11);
INSERT INTO providers_services(id_provider, id_service, price) VALUES(1, 3, 5.78);
INSERT INTO providers_services(id_provider, id_service, price) VALUES(2, 4 , 30);
INSERT INTO providers_services(id_provider, id_service, price) VALUES(2, 6 , 30);
INSERT INTO providers_services(id_provider, id_service, price) VALUES(2, 10 , 85);
INSERT INTO providers_services(id_provider, id_service, price) VALUES(3, 4, 36.42);
INSERT INTO providers_services(id_provider, id_service, price) VALUES(3, 6, 34.45);
INSERT INTO providers_services(id_provider, id_service, price) VALUES(4,6 , 32);
INSERT INTO providers_services(id_provider, id_service, price) VALUES(4, 8, 48);
INSERT INTO providers_services(id_provider, id_service, price) VALUES(5, 4, 34.45);
INSERT INTO providers_services(id_provider, id_service, price) VALUES(5, 5, 44.29);
INSERT INTO providers_services(id_provider, id_service, price) VALUES(5, 8, 53.64);
INSERT INTO providers_services(id_provider, id_service, price) VALUES(6, 11, 6.15);
INSERT INTO providers_services(id_provider, id_service, price) VALUES(6, 12, 2.44);
INSERT INTO providers_services(id_provider, id_service, price) VALUES(6, 13, 8.59);
INSERT INTO providers_services(id_provider, id_service, price) VALUES(7, 14, 32.49);

 -- populare tabela contracts
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(1, 17, to_date('24/01/2018', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(1, 6, to_date('05/07/2021', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(2, 17, to_date('09/04/2018', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(2, 7, to_date('16/09/2021', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(3, 17, to_date('06/09/2018', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(3, 9, to_date('13/10/2021', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(4, 17, to_date('05/12/2018', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(4, 14, to_date('10/11/2021', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(5, 17, to_date('06/12/2018', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(5, 10, to_date('01/12/2021', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(6, 17, to_date('01/02/2019', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(6, 5, to_date('08/12/2021', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(7, 17, to_date('27/06/2019', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(7, 4, to_date('21/01/2022', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(8, 3, to_date('08/08/2019', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(8, 17, to_date('31/03/2022', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(9, 17, to_date('30/01/2020', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(9, 16, to_date('02/05/2022', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(10, 17, to_date('06/02/2020', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(10, 8, to_date('21/02/2020', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(11, 17, to_date('03/04/2020', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(11, 1, to_date('16/02/2018', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(12, 17, to_date('15/05/2020', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(12, 14, to_date('17/08/2018', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(13, 17, to_date('15/06/2020', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(13, 12, to_date('30/09/2019', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(14, 17, to_date('21/10/2020', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(15, 17, to_date('04/01/2021', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(15, 16, to_date('31/01/2019', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(16, 17, to_date('28/06/2021', 'dd/mm/yyyy'));
INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(16, 6, to_date('04/10/2022', 'dd/mm/yyyy'));

INSERT INTO contracts(id_person, id_ps, start_date) 
VALUES(16, 6, to_date('04/10/2022', 'dd/mm/yyyy'));

INSERT INTO contracts(id_person, id_ps, start_date, end_date) 
VALUES(1, 2, to_date('04/10/2018', 'dd/mm/yyyy'), to_date('20/03/2020', 'dd/mm/yyyy'));

 -- populare tabela invoices
INSERT INTO invoices(id_contract, receipt_date, due_date, consumption)
VALUES(1, sysdate, sysdate + 14, 1);
INSERT INTO invoices(id_contract, receipt_date, due_date, consumption)
VALUES(22, sysdate, sysdate + 15, 23);
INSERT INTO invoices(id_contract, receipt_date, due_date, consumption)
VALUES(11, '10-MAR-2019', to_date('10-MAR-2019') + 15, 1);
INSERT INTO invoices(id_contract, receipt_date, due_date, consumption)
VALUES(6, '12-NOV-2021', to_date('12-NOV-2021') + 10, 1);
INSERT INTO invoices(id_contract, receipt_date, due_date, consumption)
VALUES(20, sysdate, sysdate + 13, 1);
INSERT INTO invoices(id_contract, receipt_date, due_date, consumption)
VALUES(14, '22-FEB-2022', to_date('22-FEB-2022') + 11, 1);

commit;