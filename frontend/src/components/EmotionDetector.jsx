import { useState } from "react";
import { motion } from "framer-motion";

const EmotionDetector = () => {
  const [message, setMessage] = useState("Click the button and start speaking!");
  const [emotion, setEmotion] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [audioChunks, setAudioChunks] = useState([]);

  const handleStartRecording = async () => {
    setMessage("🎙️ Recording... Speak now!");
    setEmotion("");
    setIsRecording(true);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      let chunks = [];

      recorder.ondataavailable = (event) => {
        chunks.push(event.data);
      };

      recorder.onstop = () => {
        setAudioChunks(chunks);
      };

      recorder.start();
      setMediaRecorder(recorder);
    } catch (error) {
      setMessage("🚫 Error accessing microphone!");
      console.error("Error accessing microphone:", error);
    }
  };

  const handleStopRecording = async () => {
    if (mediaRecorder) {
      mediaRecorder.stop();
      setIsRecording(false);
      setMessage("⏳ Processing audio...");

      // Convert to Blob after stop
      setTimeout(async () => {
        if (audioChunks.length > 0) {
          const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
          const formData = new FormData();
          formData.append("audio", audioBlob);

          try {
            const response = await fetch("http://127.0.0.1:5000/predict", {
              method: "POST",
              body: formData,
            });
            const data = await response.json();
            setEmotion(data.emotion);
          } catch (error) {
            setMessage("⚠️ Error analyzing emotion.");
            console.error("Error predicting emotion:", error);
          }
        }
        setMessage("Click the button and start speaking!");
      }, 1000);
    }
  };

  return (
    <div
      className="flex flex-col items-center justify-center min-h-screen p-6 bg-cover bg-center"
      style={{
        backgroundImage: "url('/voice.jpg')",
      }}
    >
      <motion.div
        className="bg-white/20 backdrop-blur-lg shadow-xl rounded-2xl p-8 text-center w-full max-w-md"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-4xl font-extrabold text-white mb-6">
          🎭 Emotion Detector
        </h1>

        {!isRecording ? (
          <motion.button
            onClick={handleStartRecording}
            className="bg-gray-400 text-black hover:font-bold px-6 py-3 rounded-full text-lg hover:bg-gray-600 hover:text-white transition cursor-pointer duration-200 shadow-lg"
            whileHover={{ scale: 0.97 }}
            whileTap={{ scale: 0.7 }}
          >
            🎤 Start Recording
          </motion.button>
        ) : (
          <motion.button
            onClick={handleStopRecording}
            className="bg-green-500 text-white font-bold px-6 py-3 rounded-full text-lg hover:bg-red-600 transition cursor-pointer duration-300 shadow-lg"
            whileHover={{ scale: 0.9 }}
            whileTap={{ scale: 0.9 }}
          >
            ⏹ Stop Recording
          </motion.button>
        )}

        <p className="mt-6 text-lg text-black font-medium">{message}</p>

        {emotion && (
          <motion.p
            className="mt-4 text-3xl font-bold text-red-600"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            {`🎭 Detected Emotion: ${emotion}`}
          </motion.p>
        )}
      </motion.div>
    </div>
  );
};

export default EmotionDetector;
