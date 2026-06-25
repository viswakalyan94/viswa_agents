CREATE TABLE hr_employee (
  employee_id NUMBER PRIMARY KEY,
  full_name VARCHAR2(100) NOT NULL,
  dept_id NUMBER NOT NULL,
  salary NUMBER(10,2),
  created_at DATE DEFAULT SYSDATE
);
