delimiter //
DROP PROCEDURE IF EXISTS sproc_product_list//

delimiter //
CREATE PROCEDURE sproc_product_list(
)
BEGIN 

/********************************************************************************
sample sproc call
call sproc_product_list()
**********************************************************************************/ 

select product_name
	,product_status
	,product_id
from product
order by product_name
;

END // 
DELIMITER ;
