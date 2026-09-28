import React, {useEffect, useState} from "react";
import { ScrollView, StyleSheet, Text, FlatList, View, Pressable } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import theme from "../constants/theme";

//type declarations
type Contact = {
  vestid: string;
  encounterstart: string;
  encounterend: string;
  encounterduration: string;
  closestdistance: string;
  latitude: string;
  longitude: string;
  altitude: string;
};

type Frequency = {
  "number of contacts per hour": number;
  "number of contacts per day": number;
  "number of contacts per week": number;
};

type DataItem = {
  contacts: Contact[];
  frequency: Frequency;
};



export default function SendReceiveDataScreen() 
{
    const LAMBDA_URL = "https://qrzb6ioqdnzlxrybtzed44lpre0piohn.lambda-url.us-east-1.on.aws/"
    const [status, setStatus] = useState("No data sent or received");
    const [display, setDisplay] = useState<DataItem[] | null>(null);
    const jsonData = {
        "vestid": 22,
    "encounterstart": "2025-10-21 08:12:15",
    "encounterend": "2025-10-21 08:12:50",
    "closestdistance": 1.42,
    "latitude": 42.3601,
    "longitude": -71.0589,
    "altitude": 50
    };
        //this function has caused me much pain and suffering
    const getUrls = async () => {
      try{
        const response = await fetch(LAMBDA_URL, {
          method: "POST",
          body: "device_test.json"
        });
      
      const result = await response.json();
      console.log('Lambda response:', result);
      
      return result;

      }catch (error) {
      console.error('Error invoking Lambda:', error);
      }
    }
    

    async function uploadJson(uploadUrl: string, data: object) {
      try{  
        const response = await fetch(uploadUrl, {
          method:"PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        });
      }catch(error){
      console.error('Error uploading to s3:', error);
      }
    }

    async function pollForResponse(downloadUrl: string) {
      while (true) {
        const response = await fetch(downloadUrl);

        if(response.ok){
          const text = await response.json(); 
          setStatus("Response Received");
          setDisplay(Array.isArray(text) ? text : [text]);
          break;
        }

        setStatus("Waiting for response from server...");
        await new Promise((resolve) => setTimeout(resolve, 2000));
      }
    }

    async function sendData(){
        try{
            const urls = await getUrls();

            const uploadUrl: string = urls.upload_url;
            const downloadUrl: string = urls.download_url;

            await uploadJson(uploadUrl, jsonData);
            await new Promise(resolve => setTimeout(resolve, 10000));
            await pollForResponse(downloadUrl);
        }
        catch (error: unknown) {
          if (error instanceof Error) {
            console.error(error);
            setStatus("Error: " + error.message);
          } 
          else {
            console.error(error);
            setStatus("Error: unknown error");
          }
}
    }

    return (
        <SafeAreaView style={STYLES.container} edges={["top", "left", "right", "bottom"]}>
        <ScrollView contentContainerStyle={STYLES.content}>
            <Text>This is a placeholder screen used for testing sending and receiving data from the server.</Text>

            <Pressable onPress={async () => { await sendData();}} style={STYLES.button}>
                <Text> Send dummy data to AWS server, receive data from server</Text>
            </Pressable>

            <Text>{status}</Text>

            {display && display[0]?.contacts?.length > 0 && (
    <>
      <Text style={{ fontSize: 20, fontWeight: "bold", marginTop: 20 }}>Contacts</Text>
      <FlatList
        data={display[0].contacts}
        keyExtractor={(item) => item.vestid}
        renderItem={({ item }) => (
          <View style={{ marginVertical: 10, padding: 10, borderWidth: 1, borderRadius: 5 }}>
            <Text>Vest ID: {item.vestid}</Text>
            <Text>Start: {item.encounterstart}</Text>
            <Text>End: {item.encounterend}</Text>
            <Text>Duration: {item.encounterduration}s</Text>
            <Text>Closest Distance: {item.closestdistance}</Text>
            <Text>Latitude: {item.latitude}</Text>
            <Text>Longitude: {item.longitude}</Text>
            <Text>Altitude: {item.altitude}</Text>
          </View>
        )}
      />

      <Text style={{ fontSize: 20, fontWeight: "bold", marginTop: 20 }}>Frequency</Text>
      <View style={{ padding: 10 }}>
        <Text>Contacts per hour: {display[0].frequency["number of contacts per hour"]}</Text>
        <Text>Contacts per day: {display[0].frequency["number of contacts per day"]}</Text>
        <Text>Contacts per week: {display[0].frequency["number of contacts per week"]}</Text>
      </View>
    </>
  )}

        </ScrollView>
        </SafeAreaView>
    );
}


const STYLES = StyleSheet.create(
{
  container: 
  { flex: 1, 
    backgroundColor: theme.colors.BACKGROUND 
  },
  content: 
  { 
    padding: theme.SPACING.LG 
  },
  title: 
  { 
    fontSize: 22, 
    fontWeight: "800", 
    color: theme.colors.PRIMARY_DARK 
  },
  subtitle: 
  { 
    fontSize: 13, 
    color: theme.colors.TEXT_MEDIUM, 
    marginBottom: 12 
  },
  cardsRow: 
  { 
    flexDirection: "row", 
    columnGap: theme.SPACING.MD 
  },
  cardDark: 
  {
    flex: 1,
    backgroundColor: theme.colors.PRIMARY_DARK,
    borderRadius: theme.RADIUS.MD,
    padding: theme.SPACING.MD,
  },
  button: {
    paddingVertical: 14,
    paddingHorizontal: 20,
    borderRadius: 10,
    alignItems: "center",
  },
  cardLabelLight: 
  { 
    fontSize: 12, 
    color: theme.colors.PRIMARY_LIGHT 
  },
  cardValueLight: 
  { 
    marginTop: 4, 
    fontSize: 22, 
    fontWeight: "800", 
    color: theme.colors.BACKGROUND 
  },
  card: 
  {
    flex: 1,
    backgroundColor: "#fff",
    borderRadius: theme.RADIUS.MD,
    padding: theme.SPACING.MD,
    borderWidth: 1,
    borderColor: theme.colors.PRIMARY_LIGHT,
  },
  cardLabel: 
  { 
    fontSize: 12, 
    color: theme.colors.TEXT_MEDIUM 
  },
  cardValue: 
  { 
    marginTop: 4, 
    fontSize: 22, 
    fontWeight: "800", 
    color: theme.colors.PRIMARY_DARK 
  },
});
