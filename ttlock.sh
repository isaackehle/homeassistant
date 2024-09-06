
CLIENT_ID=1a27af8858154fefa016a425e3422464
CLIENT_SECRET=b27615d96b93d289b14943596a362b03
IOS_USERNAME=isaac.kehle@gmail.com
PASS_IN_MD5_FORMAT=db31ccba60d665c23769fedf7a2290d6 # `md5 -s 'pooh-hallow-TOM-23()'`

curl -i -X POST -d “clientId=$CLIENT_ID&clientSecret=$CLIENT_SECRET&username=IOS_USERNAME&password=PASS_IN_MD5_FORMAT&date=date +%s” https://api.ttlock.com/v3/user/register 86

$ curl --location --request POST "https://api.ttlock.com/v3/user/register?clientId=$CLIENT_ID&clientSecret=CLIENT_SECRET&username=isaac.kehle@gmail.com&password=put here the password md5 decrypted for account at site&date=CURRENTMILLIS" \
--header 'Content-Type: application/x-www-form-urlencoded' \



curl --location -g --request POST 'https://api.ttlock.com/oauth2/token' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode "clientId=$CLIENT_ID" \
--data-urlencode "clientSecret=$CLIENT_SECRET" \
--data-urlencode "username=$IOS_USERNAME" \
--data-urlencode "password=$PASS_IN_MD5_FORMAT"


{"access_token":"19185be30c568f8417b46951fef23c19","uid":24997130,"refresh_token":"ee4c8448fb2b2940543d10e890097e32","openid":1730236178,"scope":"user,key,room","token_type":"Bearer","expires_in":7776000}%


# oauth2
# clientId: MD5 ("Twenty4Wasa_good_show") = 90b06fdc3cb68befb143cadd85f4cf72
# clientSecret: MD5 ("BackToLifeBackToReality") = fe12e1f59bd6275d7f3c44fe749f6c18