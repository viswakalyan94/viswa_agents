CREATE OR REPLACE TRIGGER hr_employee_audit_trg
BEFORE INSERT OR UPDATE ON hr_employee
FOR EACH ROW
BEGIN
  IF :NEW.employee_id IS NULL THEN
    :NEW.employee_id := hr_employee_seq.NEXTVAL;
  END IF;
END;
/
