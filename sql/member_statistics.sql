/*Member count*/
SELECT COUNT(*) FROM ~members~

/*have hometown*/
SELECT COUNT(*) FROM ~members~ WHERE hometown IS NOT NULL

/*city != hometown*/
SELECT COUNT(*) FROM ~members~ WHERE hometown != city

/*have bio*/
SELECT COUNT(*) FROM ~members~ WHERE bio IS NOT NULL

/*avg length of bio*/
SELECT AVG(LENGTH(bio)) FROM ~members~ WHERE bio IS NOT NULL

/*median length of bio*/
SELECT MEDIAN(LENGTH(bio)) FROM ~members~ WHERE bio IS NOT NULL