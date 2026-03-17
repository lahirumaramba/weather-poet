import { googleAI } from "@genkit-ai/google-genai";
import { genkit, z } from "genkit";
import { enableFirebaseTelemetry } from "@genkit-ai/firebase";
import { onCallGenkit } from "firebase-functions/https";
import { defineSecret } from "firebase-functions/params";

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
  model: "googleai/gemini-2.5-flash", // set default model
});

const getWeather = async (
  location: string
): Promise<Record<string, unknown>> => {
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
  name: z.string().optional(),
  country: z.string().optional(),
  last_updated: z.string().optional(),
  temp_c: z.number().optional(),
  condition_text: z.string().optional(),
  wind_dir: z.string().optional(),
  wind_kph: z.number().optional(),
  feelslike_c: z.number().optional(),
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
  async ({ location, tone }) => {
    let weatherInfo;
    try {
      weatherInfo = await getWeather(location);
    } catch (error) {
      console.error("Error fetching or parsing wearher data:", error);
      return { text: `Error: ${error}` };
    }
    // Make it sound genz:
    const { text } = await ai.generate({
      system: `You are a world famous poet.
        Please use the provided weather data to write a 
        short poem to describe the weather.
        Use creative words. Keep it short and bright.
        Only respond with the poem and nothing else.`,
      prompt: `Write a short poem to describe this weather.${tone ? ` Make it sound ${tone}` : ""
        }:
        \`\`\`json
        ${JSON.stringify(weatherInfo)}
        \`\`\``,
    });
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const info = weatherInfo as any;
    return {
      text,
      name: info?.location?.name,
      country: info?.location?.country,
      last_updated: info?.current?.last_updated,
      temp_c: info?.current?.temp_c,
      condition_text: info?.current?.condition?.text,
      wind_dir: info?.current?.wind_dir,
      wind_kph: info?.current?.wind_kph,
      feelslike_c: info?.current?.feelslike_c,
    };
  }
);

const authCallback = (
  auth?: { uid: string } | null,
  _data?: unknown
): boolean => {
  return auth?.uid == uid.value();
};

export const generatePoem = onCallGenkit(
  {
    secrets: [genAIApiKey, weatherApiKey, uid],
    authPolicy: authCallback,
  },
  generatePoemFlow
);
