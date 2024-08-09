BEGIN TRANSACTION;

INSERT INTO suppliers VALUES (35897, 'Lincat');

INSERT INTO automations VALUES (1, 0, 'https://www.dropbox.com/scl/fo/esslg14rtd60zbtbzrb9d/APrFQ7IESdlNCKAeqXaepYk?rlkey=tes3ysvrsshupu9rd9zdco120&e=1&dl=0', '83475173jwegbfby228ur8', 'Dropbox Stock', NULL, 35897);

INSERT INTO steps VALUES (1, '[{"action": "playwright_goto", "pw_arg": "", "pw_arg_2": "", "url": "https://www.dropbox.com/scl/fo/esslg14rtd60zbtbzrb9d/APrFQ7IESdlNCKAeqXaepYk?rlkey=tes3ysvrsshupu9rd9zdco120&e=1&dl=0"}, {"action": "playwright_click", "method": "text", "pw_arg": "Download", "pw_arg_2": ""}, {"action": "playwright_click_download", "method": "text", "pw_arg": "Or continue with download only", "pw_arg_2": ""}]');

COMMIT;