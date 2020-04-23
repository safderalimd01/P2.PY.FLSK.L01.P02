delimiter //
DROP PROCEDURE IF EXISTS sproc_product_list_by_active_status//

delimiter //
CREATE PROCEDURE sproc_product_list_by_active_status(
IN iparam_product_status tinyint,

OUT oparam_err_flag int,
OUT oparam_err_step varchar(100),
OUT oparam_err_msg varchar(1000)
)
BEGIN 

/********************************************************************************
-- sample call:
set @iparam_product_status = 0;

call sproc_product_list_by_active_status
(@iparam_product_status

,@oparam_err_flag 
,@oparam_err_step 
,@oparam_err_msg);

select @oparam_err_flag, @oparam_err_step, @oparam_err_msg;
**********************************************************************************/

-- step 10
-- declare variables
declare  v_step_number int;

DECLARE exit handler for sqlexception , sqlwarning
BEGIN
     
	 ROLLBACK;

	 GET DIAGNOSTICS CONDITION 1 @sqlstate = RETURNED_SQLSTATE, 
	 @errno = MYSQL_ERRNO, @errtext = MESSAGE_TEXT;

	set oparam_err_flag = 1;

	set oparam_err_step  = concat('error in step: ',v_step_number);

	set oparam_err_msg = @errtext;

END;  

-- step 20
-- initialize
set v_step_number = 20;
set oparam_err_flag = 0;

 -- step 30
-- pull data
set v_step_number = 30;

select product_name
	-- ,active
	,product_id
from product
where product_status  = iparam_product_status
order by product_name
;

END // 
DELIMITER ;
