import {gemini20Flash, googleAI} from "@genkit-ai/googleai";
import {genkit, z} from "genkit";
import {enableFirebaseTelemetry} from "@genkit-ai/firebase";
import {onCallGenkit} from "firebase-functions/https";
import {defineSecret} from "firebase-functions/params";

enableFirebaseTelemetry();

const genAIApiKey = defineSecret("GOOGLE_GENAI_API_KEY");
const weatherApiKey = defineSecret("WEATHER_API_KEY");
const uid = defineSecret("UID");

const options = {
  method: "GET",
  headers: {
    "accept": "application/json",
    "accept-encoding": "deflate, gzip, br",
  },
};

const ai = genkit({
  plugins: [googleAI()],
  model: gemini20Flash, // set default model
});

const getWeather = async (location: string): Promise<any> => {
  const weatherURL = `http://api.weatherapi.com/v1/current.json?key=${weatherApiKey.value()}&aqi=no&q=${location}`;
  try {
    const response = await fetch(weatherURL, options);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const weatherData = await response.json();
    return weatherData;
  } catch (error) {
    console.error("Error fetching or parsing:", error);
    throw error;
  }
};

const PoemSchema = z.object({
  text: z.string(),
  icon: z.string(),
});

const InputSchema = z.object({
  location: z.string(),
  tone: z.string(),
});

const generatePoemFlow = ai.defineFlow(
  {
    name: "generatePoem",
    inputSchema: InputSchema,
    outputSchema: PoemSchema,
  },
  async ({location, tone}) => {
    let weatherInfo; let weatherIcon;
    try {
      weatherInfo = await getWeather(location);
      weatherIcon = weatherInfo?.current?.condition?.icon;
    } catch (error) {
      console.error("Error fetching or parsing wearher data:", error);
      return {text: `Error: ${error}`, icon: "error"};
    }
    // Make it sound genz:
    const {text} = await ai.generate({
      system: `You are a world famous poet.
        Please use the provided weather data to write a 
        short poem to describe the weather.
        Use creative words. Keep it short and bright.
        Only respond with the poem and nothing else.`,
      prompt: `Write a short poem to describe this weather.${
        tone ? ` Make it sound ${tone}` : ""
      }:
        \`\`\`json
        ${JSON.stringify(weatherInfo)}
        \`\`\``,
    });
    return {text, icon: weatherIcon};
  }
);

const authCallback = (auth: any, data: any): boolean => {
  return auth?.uid == uid.value();
};

export const generatePoem = onCallGenkit(
  {
    secrets: [genAIApiKey, weatherApiKey, uid],
    authPolicy: authCallback,
  },
  generatePoemFlow
);
