import React, { useState } from "react";
import { getSchedule, logTaskAction } from "../services/api";
import { motion, AnimatePresence } from "framer-motion";
import Confetti from "react-confetti";
import { useWindowSize } from "@uidotdev/usehooks";

function SchedulePage({ token, userId, onLogout, onReset }) {
  const [taskText, setTaskText] = useState("");
  const [time, setTime] = useState("120");
  const [schedule, setSchedule] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [done, setDone] = useState(false);
  const [showExtendInput, setShowExtendInput] = useState(false);
  const [extendMinutes, setExtendMinutes] = useState("");
  const { width, height } = useWindowSize();

  const handleSchedule = async () => {
    const data = await getSchedule(token, taskText, parseInt(time));
    setSchedule(data.schedule);
    setCurrentIndex(0);
    setDone(false);
  };

  const handleAction = async (action) => {
    const task = schedule[currentIndex];
    if (action === "e") {
      setShowExtendInput(true);
      return;
    }

    await logTaskAction(token, userId, task, action, null);

    if (action === "d") {
      const newSchedule = [...schedule];
      newSchedule.push(newSchedule.splice(currentIndex, 1)[0]);
      setSchedule(newSchedule);
    } else if (currentIndex + 1 >= schedule.length) {
      setDone(true);
    } else {
      setCurrentIndex((i) => i + 1);
    }
  };

  const handleExtendApply = async () => {
    const extra = parseInt(extendMinutes);
    if (isNaN(extra) || extra <= 0) {
      alert("Please enter a valid number of minutes.");
      return;
    }

    const task = schedule[currentIndex];
    task.duration += extra;
    await logTaskAction(token, userId, task, "e", extra);

    setShowExtendInput(false);
    setExtendMinutes("");

    if (currentIndex + 1 >= schedule.length) {
      setDone(true);
    } else {
      setCurrentIndex((i) => i + 1);
    }
  };

  const progressPercent = schedule.length
    ? ((currentIndex + (done ? 1 : 0)) / schedule.length) * 100
    : 0;

  if (schedule.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-100 to-sky-200 px-4">
        <div className="bg-white w-full max-w-xl p-8 rounded-3xl shadow-xl border border-indigo-100">
          <h2 className="text-3xl font-bold text-indigo-700 mb-6 text-center">Create Your Study Schedule</h2>

          <label className="block text-sm font-medium text-gray-700 mb-1">Tasks</label>
          <textarea
            rows={4}
            value={taskText}
            onChange={(e) => setTaskText(e.target.value)}
            placeholder="e.g. Watch 3 videos, do 2 homework, 1 leetcode"
            className="w-full mb-4 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-300"
          />

          <label className="block text-sm font-medium text-gray-700 mb-1">Available Time (minutes)</label>
          <input
            value={time}
            onChange={(e) => setTime(e.target.value)}
            className="w-full mb-6 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-300"
            placeholder="120"
          />

          <button
            onClick={handleSchedule}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-lg font-semibold transition-all shadow-md hover:shadow-lg"
          >
            Generate Schedule
          </button>
        </div>
      </div>
    );
  }

  if (done) {
    return (
      <div className="min-h-screen flex flex-col gap-4 items-center justify-center bg-gradient-to-br from-indigo-100 to-sky-200 px-4 text-center">
        <Confetti width={width} height={height} />
        <h3 className="text-4xl font-bold text-indigo-700 animate-bounce">All tasks complete!</h3>
        <div className="flex flex-col sm:flex-row gap-4 mt-6">
          <button
            onClick={() => {
              setTaskText("");
              setSchedule([]);
              setDone(false);
              if (typeof onReset === "function") onReset();
            }}
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg shadow-md"
          >
            Create Another Schedule
          </button>
          <button
            onClick={() => {
              if (typeof onLogout === "function") onLogout();
            }}
            className="bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-lg shadow-md"
          >
            Log Out
          </button>
        </div>
      </div>
    );
  }

  const currentTask = schedule[currentIndex];

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-indigo-100 to-sky-200 px-4">
      <div className="w-full max-w-xl mb-4 h-2 rounded-full bg-indigo-100 overflow-hidden">
        <div
          className="h-full bg-indigo-500 transition-all duration-500"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={currentTask.task_id}
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -30 }}
          transition={{ duration: 0.3 }}
          className="bg-white w-full max-w-xl p-8 rounded-3xl shadow-xl border border-indigo-100"
        >
          <h2 className="text-xl font-semibold text-indigo-700 mb-2">Current Task</h2>
          <p className="text-lg font-medium mb-6 text-gray-800">
            {currentTask.description}{" "}
            <span className="text-sm text-gray-500">({Math.round(currentTask.duration)} mins)</span>
          </p>

          {showExtendInput && (
            <div className="mt-4 bg-indigo-50 border border-indigo-200 p-4 rounded-lg shadow-sm">
              <label className="block text-sm font-medium text-indigo-700 mb-1">
                Add extra time (minutes)
              </label>
              <input
                type="number"
                value={extendMinutes}
                onChange={(e) => setExtendMinutes(e.target.value)}
                className="w-full p-2 border border-indigo-300 rounded-md mb-3"
                placeholder="e.g. 10"
              />
              <div className="flex justify-center gap-2">
                <button
                  onClick={handleExtendApply}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md"
                >
                  Apply
                </button>
                <button
                  onClick={() => {
                    setShowExtendInput(false);
                    setExtendMinutes("");
                  }}
                  className="bg-gray-400 hover:bg-gray-500 text-white px-4 py-2 rounded-md"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {!showExtendInput && (
            <div className="flex flex-wrap gap-3 justify-center">
              <button
                onClick={() => handleAction("c")}
                className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg"
              >
                ✅ Complete
              </button>
              <button
                onClick={() => handleAction("s")}
                className="bg-yellow-400 hover:bg-yellow-500 text-white px-4 py-2 rounded-lg"
              >
                ⏭ Skip
              </button>
              <button
                onClick={() => handleAction("d")}
                className="bg-gray-400 hover:bg-gray-500 text-white px-4 py-2 rounded-lg"
              >
                ↪️ Defer
              </button>
              <button
                onClick={() => handleAction("e")}
                className="bg-indigo-500 hover:bg-indigo-600 text-white px-4 py-2 rounded-lg"
              >
                ➕ Extend
              </button>
            </div>
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}

export default SchedulePage;
