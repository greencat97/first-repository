CREATE DATABASE IF NOT EXISTS uv_skin_db;
USE uv_skin_db;

DROP TABLE IF EXISTS uv_skin_data;

CREATE TABLE uv_skin_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fitzpatrick_phototype VARCHAR(50),
    phenotype TEXT,
    epidermal_eumelanin VARCHAR(100),
    cutaneous_response_to_uv TEXT,
    med_mj_cm2 VARCHAR(50),
    cancer_risk_out_of_4 VARCHAR(20)
);


INSERT INTO uv_skin_data
(fitzpatrick_phototype, phenotype, epidermal_eumelanin, cutaneous_response_to_uv, med_mj_cm2, cancer_risk_out_of_4)
VALUES
('I', 'Unexposed skin is bright white', '+/−', 'Always Burns', '15-30', '4.0');


INSERT INTO uv_skin_data
(fitzpatrick_phototype, phenotype, epidermal_eumelanin, cutaneous_response_to_uv, med_mj_cm2, cancer_risk_out_of_4)
VALUES
('I', 'Blue/green eyes typical', '+/−', 'Peels', '15-30', '4.0');


INSERT INTO uv_skin_data
(fitzpatrick_phototype, phenotype, epidermal_eumelanin, cutaneous_response_to_uv, med_mj_cm2, cancer_risk_out_of_4)
VALUES
('I', 'Freckling frequent', '+/−', 'Never tans', '15-30', '4.0');


INSERT INTO uv_skin_data
(fitzpatrick_phototype, phenotype, epidermal_eumelanin, cutaneous_response_to_uv, med_mj_cm2, cancer_risk_out_of_4)
VALUES
('I', 'Northern European/British', '+/−', NULL, '15-30', '4.0');


INSERT INTO uv_skin_data
(fitzpatrick_phototype, phenotype, epidermal_eumelanin, cutaneous_response_to_uv, med_mj_cm2, cancer_risk_out_of_4)
VALUES
('II', 'Unexposed skin is white', '+', 'Burns easily', '25-40', '3.5');


INSERT INTO uv_skin_data
(fitzpatrick_phototype, phenotype, epidermal_eumelanin, cutaneous_response_to_uv, med_mj_cm2, cancer_risk_out_of_4)
VALUES
('II', 'Blue, hazel or brown eyes', '+', 'Peels', '25-40', '3.5');


INSERT INTO uv_skin_data
(fitzpatrick_phototype, phenotype, epidermal_eumelanin, cutaneous_response_to_uv, med_mj_cm2, cancer_risk_out_of_4)
VALUES
('II', 'Red, blonde or brown hair', '+', 'Tans minimally', '25-40', '3.5');


INSERT INTO uv_skin_data
(fitzpatrick_phototype, phenotype, epidermal_eumelanin, cutaneous_response_to_uv, med_mj_cm2, cancer_risk_out_of_4)
VALUES
('II', 'European/Scandinavian', '+', NULL, '25-40', '3.5');


INSERT INTO uv_skin_data
(fitzpatrick_phototype, phenotype, epidermal_eumelanin, cutaneous_response_to_uv, med_mj_cm2, cancer_risk_out_of_4)
VALUES
('III', 'Unexposed skin is fair', '++', 'Burns moderately', '30-50', '3.0');


INSERT INTO uv_skin_data
(fitzpatrick_phototype, phenotype, epidermal_eumelanin, cutaneous_response_to_uv, med_mj_cm2, cancer_risk_out_of_4)
VALUES
('III', 'Brown eyes', '++', 'Average tanning ability', '30-50', '3.0');


INSERT INTO uv_skin_data
(fitzpatrick_phototype, phenotype, epidermal_eumelanin, cutaneous_response_to_uv, med_mj_cm2, cancer_risk_out_of_4)
VALUES
('III', 'Dark hair', '++', NULL, '30-50', '3.0');


INSERT INTO uv_skin_data
(fitzpatrick_phototype, phenotype, epidermal_eumelanin, cutaneous_response_to_uv, med_mj_cm2, cancer_risk_out_of_4)
VALUES
('III', 'Southern or Central European', '++', NULL, '30-50', '3.0');


INSERT INTO uv_skin_data
(fitzpatrick_phototype, phenotype, epidermal_eumelanin, cutaneous_response_to_uv, med_mj_cm2, cancer_risk_out_of_4)
VALUES
('IV', 'Unexposed skin is light brown', '+++', 'Burns minimally', '40-60', '2.0');


INSERT INTO uv_skin_data
(fitzpatrick_phototype, phenotype, epidermal_eumelanin, cutaneous_response_to_uv, med_mj_cm2, cancer_risk_out_of_4)
VALUES
('IV', 'Dark eyes', '+++', 'Tans easily', '40-60', '2.0');


INSERT INTO uv_skin_data
(fitzpatrick_phototype, phenotype, epidermal_eumelanin, cutaneous_response_to_uv, med_mj_cm2, cancer_risk_out_of_4)
VALUES
('IV', 'Dark hair', '+++', NULL, '40-60', '2.0');


INSERT INTO uv_skin_data
(fitzpatrick_phototype, phenotype, epidermal_eumelanin, cutaneous_response_to_uv, med_mj_cm2, cancer_risk_out_of_4)
VALUES
('IV', 'Mediterranean, Asian or Latino', '+++', NULL, '40-60', '2.0');


INSERT INTO uv_skin_data
(fitzpatrick_phototype, phenotype, epidermal_eumelanin, cutaneous_response_to_uv, med_mj_cm2, cancer_risk_out_of_4)
VALUES
('V', 'Unexposed skin is brown', '++++', 'Rarely burns', '60-90', '1.0');


INSERT INTO uv_skin_data
(fitzpatrick_phototype, phenotype, epidermal_eumelanin, cutaneous_response_to_uv, med_mj_cm2, cancer_risk_out_of_4)
VALUES
('V', 'Dark eyes', '++++', 'Tans easily and substantially', '60-90', '1.0');


INSERT INTO uv_skin_data
(fitzpatrick_phototype, phenotype, epidermal_eumelanin, cutaneous_response_to_uv, med_mj_cm2, cancer_risk_out_of_4)
VALUES
('V', 'Dark hair', '++++', NULL, '60-90', '1.0');


INSERT INTO uv_skin_data
(fitzpatrick_phototype, phenotype, epidermal_eumelanin, cutaneous_response_to_uv, med_mj_cm2, cancer_risk_out_of_4)
VALUES
('V', 'East Indian, Native American,', '++++', NULL, '60-90', '1.0');


INSERT INTO uv_skin_data
(fitzpatrick_phototype, phenotype, epidermal_eumelanin, cutaneous_response_to_uv, med_mj_cm2, cancer_risk_out_of_4)
VALUES
('V', 'Latino or African', '++++', NULL, '60-90', '1.0');


INSERT INTO uv_skin_data
(fitzpatrick_phototype, phenotype, epidermal_eumelanin, cutaneous_response_to_uv, med_mj_cm2, cancer_risk_out_of_4)
VALUES
('VI', 'Unexposed skin is black', '+++++', 'Almost never burns', '90-150', '0.5');


INSERT INTO uv_skin_data
(fitzpatrick_phototype, phenotype, epidermal_eumelanin, cutaneous_response_to_uv, med_mj_cm2, cancer_risk_out_of_4)
VALUES
('VI', 'Dark eyes', '+++++', 'Tans readily and profusely', '90-150', '0.5');


INSERT INTO uv_skin_data
(fitzpatrick_phototype, phenotype, epidermal_eumelanin, cutaneous_response_to_uv, med_mj_cm2, cancer_risk_out_of_4)
VALUES
('VI', 'Dark hair', '+++++', NULL, '90-150', '0.5');


INSERT INTO uv_skin_data
(fitzpatrick_phototype, phenotype, epidermal_eumelanin, cutaneous_response_to_uv, med_mj_cm2, cancer_risk_out_of_4)
VALUES
('VI', 'African or Aboriginal ancestry', '+++++', NULL, '90-150', '0.5');
