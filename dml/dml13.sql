-- Повышение арендной платы
UPDATE rentals
SET rent_amount = rent_amount * 1.08
WHERE lease_end_date > NOW() AND location = 'Downtown';
