The idea behind this project is to create a wearable vest with motion sensing technology capable of determining when the wearer comes within ~6
feet of another person. A Raspberry Pi on the vest then sends a data packet via Bluetooth to the wearer's phone, which is then sent via Wi-Fi or mobile data
through the companion app to an AWS server where information about the encounter is automatically stored in an SQL server.

For my part in this project, I handled the back end, primarily the sending of data via Bluetooth to the mobile phone, using a combination of Python and 
Java (React Native) and then the sending of data via Wi-Fi or mobile data to the AWS server using Java (React Native) as well as several AWS tools (S3, SQS, Lambda), 
where the data was automatically placed into an SQL server using a python script.
