import React, { useEffect, useState, useRef, useMemo } from "react";
import mqtt from "mqtt";
import { ResponsiveContainer, LineChart, CartesianGrid, XAxis, YAxis, Tooltip, Legend, Line } from "recharts";
import config from "./config"; // 引入 MQTT 配置
import html2canvas from "html2canvas"; // Import html2canvas
import Cookies from "js-cookie"; // Ensure you have js-cookie installed

const MqttPage = () => {
    // State variables
    const [instantFlow, setInstantFlow] = useState(0); // Real-time flow value
    const [relayStatus, setRelayStatus] = useState({}); // Relay statuses
    const [heaterTemp, setHeaterTemp] = useState({ temp1: 0, temp2: 0, temp3: 0, temp4: 0 });
    const [heaterStage, setHeaterStage] = useState(""); // Heater cycle stage info

    // State for the temperature chart
    const [chartData, setChartData] = useState([]);
    const [cmdRawList, setCmdRawList] = useState([]); // Store raw command messages
    const [heaterDataStatus, setHeaterDataStatus] = useState("溫度偵測正常"); // Default is normal
    // Tracks the last time we received good data
    const lastUpdateRef = useRef(Date.now()); // ✅ Use ref instead of state

    const [relayDataStatus, setRelayDataStatus] = useState("繼電器偵測正常"); // Default: Normal
    const lastRelayUpdateRef = useRef(Date.now()); // ✅ Tracks last update time for usbrelay/state

    // const [lastHeaterUpdateTime, setLastHeaterUpdateTime] = useState(Date.now());
    const startTimeRef = useRef(null); // ✅ Use useRef instead of useState

    const mqttClient = useRef(null);

    // 從 config.js 讀取 MQTT 配置
    const { mqttHost, mqttUsername, mqttPassword } = config;
    const [isDrawing, setIsDrawing] = useState(false); // Only draw during auto test
    const [toastMessage, setToastMessage] = useState(""); // Store the message

    const tempLabels = { 1: "H", 2: "M", 3: "L", 4: "R" };


    const [showExtraLines, setShowExtraLines] = useState(false);




    const isDrawingRef = useRef(false);

    const cmdListRef = useRef(null);
    const heaterStageRef = useRef(""); // ✅ Store the latest heaterStage
    const [drawingCompleted, setDrawingCompleted] = useState(false);

    const [temp1Error, setTemp1Error] = useState(false);

    // New state for filename
    const [filename, setFilename] = useState("");


    const testCompletedRef = useRef(false);

    // Function to get initial temperature offset from cookies (default 0)
    const getInitialTempOffset = () => {
        const storedOffset = Cookies.get("TEMP_OFFSET");
        return storedOffset ? parseInt(storedOffset, 10) || 0 : 0;
    };

    const [tempOffset, setTempOffset] = useState(getInitialTempOffset());

    // Watch for changes and update cookies
    useEffect(() => {
        console.log("Temperature Offset Updated:", tempOffset);
        Cookies.set("TEMP_OFFSET", tempOffset, { expires: 365 });
    }, [tempOffset]);

    // Function to update offset
    const updateTempOffset = (newOffset) => {
        if (!isNaN(newOffset)) {
            setTempOffset(newOffset);
        }
    };

    // Apply the offset when displaying or saving temperature
    const adjustedHeaterTemp = {
        temp1: heaterTemp.temp1 + tempOffset,
        temp2: heaterTemp.temp2 + tempOffset,
        temp3: heaterTemp.temp3 + tempOffset,
        temp4: heaterTemp.temp4 + tempOffset,
    };



    function saveChartWithTimestamp(chartData, filename) {
        const tempLabels = { 1: "H", 2: "M", 3: "L", 4: "R" };

        // Get Taiwan Time (UTC+8)
        const now = new Date();
        const taiwanTime = new Intl.DateTimeFormat("zh-TW", {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
            hour12: false,
            timeZone: "Asia/Taipei",
        })
            .format(now)
            .replace(/\//g, "-")
            .replace(/ /g, "_")
            .replace(/:/g, "-");

        // Generate file name
        const filenameSuffix = filename ? `_${filename}` : "";
        const baseFilename = `${taiwanTime}${filenameSuffix}`;

        // Find the chart element
        const chartElement = document.querySelector(".recharts-wrapper");
        if (!chartElement) {
            console.error("❌ Chart element not found");
            return;
        }

        console.log("✅ Capturing chart as image...");
        html2canvas(chartElement, { scale: 2 })
            .then((canvas) => {
                canvas.toBlob((blob) => {
                    if (!blob) {
                        console.error("❌ Blob creation failed");
                        setToastMessage(
                            <p className="text-center text-red-600">
                                截圖失敗：無法創建圖像Blob
                            </p>
                        );
                        return;
                    }

                    // Apply the offset when saving chart data
                    const mappedChartData = chartData.map((dataPoint) => ({
                        time: dataPoint.time,
                        timestamp: dataPoint.timestamp,
                        temp1: (dataPoint.temp1 ?? 0) + tempOffset,
                        temp2: (dataPoint.temp2 ?? 0) + tempOffset,
                        temp3: (dataPoint.temp3 ?? 0) + tempOffset,
                        temp4: (dataPoint.temp4 ?? 0) + tempOffset,
                        stage: dataPoint.stage,
                        hasError: dataPoint.hasError,
                    }));

                    const jsonBlob = new Blob([JSON.stringify(mappedChartData, null, 2)], {
                        type: "application/json",
                    });

                    // Create FormData and append files and project
                    const formData = new FormData();
                    formData.append("file", blob, `${baseFilename}.png`);
                    formData.append("json_file", jsonBlob, `${baseFilename}.json`);
                    formData.append("project", "heater");

                    console.log("🚀 Uploading files...");
                    fetch("http://localhost:8000/upload_file", {
                        method: "POST",
                        body: formData,
                    })
                        .then((response) => {
                            if (!response.ok) {
                                throw new Error(`HTTP error! Status: ${response.status}`);
                            }
                            return response.json();
                        })
                        .then((data) => {
                            console.log("✅ 儲存成功:", data);
                            const imageFilename = data.image_filename || `${baseFilename}.png`;
                            const jsonFilename = data.json_filename || `${baseFilename}.json`;
                            setToastMessage(
                                <div className="text-center">
                                    <p>📤 圖片與圖表數據儲存成功！</p>
                                    <p className="text-xs mt-1 text-left">
                                        檔案夾: <span className="font-mono">heater</span>
                                        <br />
                                        圖片: <span className="font-mono">{imageFilename}</span>
                                        <br />
                                        JSON: <span className="font-mono">{jsonFilename}</span>
                                    </p>
                                </div>
                            );
                        })
                        .catch((error) => {
                            console.error("❌ Upload failed:", error);
                            setToastMessage(
                                <p className="text-center text-red-600">
                                    儲存失敗: {error.message}
                                </p>
                            );
                        });
                }, "image/png");
            })
            .catch((error) => {
                console.error("❌ Error capturing chart as image:", error);
                setToastMessage(
                    <p className="text-center text-red-600">
                        截圖失敗: {error.message}
                    </p>
                );
            });
    }



    useEffect(() => {
        if (heaterTemp?.temp1 !== undefined && heaterTemp?.temp1 < 15) {
            setTemp1Error(true); // ✅ Set error state if temp1 is below 15
        } else {
            setTemp1Error(false); // ✅ Clear error if temp1 is valid
        }
    }, [heaterTemp?.temp1]); // ✅ Runs whenever temp1 updates


    useEffect(() => {
        if (!isDrawing && isDrawingRef.current && chartData.length > 0) {
            setDrawingCompleted(true);
        }
        isDrawingRef.current = isDrawing;
    }, [isDrawing, chartData]);  // ✅ Remove `filename` dependency to trigger properly


    useEffect(() => {
        const timer = setInterval(() => {
            const timeSinceLastRelayUpdate = Date.now() - lastRelayUpdateRef.current; // ✅ Get elapsed time

            if (timeSinceLastRelayUpdate > 1000) {
                setRelayDataStatus("繼電器傳輸錯誤,請檢查USB連線,無法測試"); // 🔴 Set error if no data received
            } else {
                setRelayDataStatus("繼電器偵測正常"); // 🟢 Normal
            }
        }, 1000);

        return () => clearInterval(timer);
    }, []); // ✅ Runs continuously

    useEffect(() => {
        heaterStageRef.current = heaterStage; // ✅ Always store the latest value
    }, [heaterStage]);

    // Simulate receiving data to reset the timer
    useEffect(() => {
        if (cmdListRef.current) {
            cmdListRef.current.scrollTop = cmdListRef.current.scrollHeight;
        }
    }, [cmdRawList]);

    useEffect(() => {
        isDrawingRef.current = isDrawing; // ✅ Always update ref
    }, [isDrawing]);

    const TOPIC_FLOW = "air/flow";
    const TOPIC_USB_STAT = "usbrelay/state/#";
    const TOPIC_HEATER_CMD = "autotest/heat3";
    const TOPIC_HEATER_TEMP = "heater/temperature";
    const TOPIC_HEATER_STAT = "heater/stage";

    // Mapping for relay names
    const relayNames = {
        QAAMZ_2: "全開",
        QAAMZ_3: "左側",
        QAAMZ_1: "右側",
    };

    useEffect(() => {
        const timer = setInterval(() => {
            const timeSinceLastUpdate = Date.now() - lastUpdateRef.current; // ✅ Correct usage

            // console.log("Checking timeSinceLastUpdate:", timeSinceLastUpdate);
            // console.log("lastUpdateRef.current:", lastUpdateRef.current); // ✅ Log the ref

            if (timeSinceLastUpdate > 1000) {
                setHeaterDataStatus("溫度偵測錯誤,請檢查USB連線,無法測試"); // 🔴 Red
            } else {
                setHeaterDataStatus("溫度偵測正常"); // 🟢 Green
            }
        }, 1000);

        return () => clearInterval(timer);
    }, []); // ✅ No dependencies needed since `lastUpdateRef` doesn't trigger re-renders

    useEffect(() => {
        if (heaterStage === "啟動中") {
            setIsDrawing(true);
            startTimeRef.current = Date.now(); // ✅ Store start time correctly
        } else if (heaterStage === "關閉左右側氣道,測試結束") {
            setIsDrawing(false);
        }
    }, [heaterStage]);

    useEffect(() => {
        if (drawingCompleted) {
            console.log("Drawing completed! Save button is now visible.");
        }
    }, [drawingCompleted]); // ✅ Runs whenever `drawingCompleted` changes


    useEffect(() => {
        const connectToMqtt = () => {
            const client = mqtt.connect(mqttHost, {
                username: mqttUsername,
                password: mqttPassword,
                reconnectPeriod: 1000,
            });

            client.on("connect", () => {
                console.log("Connected to MQTT broker");
                client.subscribe(
                    [
                        TOPIC_FLOW,
                        TOPIC_USB_STAT,
                        TOPIC_HEATER_TEMP,
                        TOPIC_HEATER_STAT,
                        // TOPIC_HEATER_CMD,
                        "heater/cmd_raw" // Subscribe to heater/cmd_raw
                    ],
                    (err) => {
                        if (err) console.error("Subscription error:", err);
                    }
                );
            });

            client.on("message", (topic, message) => {
                let payload; // ✅ Define payload first

                try {
                    payload = message.toString(); // Convert to string first

                    // Try to parse as JSON if it's a valid JSON object
                    if (payload.startsWith("{") && payload.endsWith("}")) {
                        payload = JSON.parse(payload);
                    } else {
                        // console.warn("Non-JSON payload received:", payload);
                    }
                } catch (error) {
                    console.error("Error parsing MQTT payload:", error);
                }

                if (!payload) return; // ✅ Prevent undefined errors
                // ✅ Update `lastUpdate` every time we get new data
                // setLastUpdate(Date.now());

                if (topic.startsWith("usbrelay/state/")) {
                    lastRelayUpdateRef.current = Date.now(); // ✅ Update timestamp when relay data arrives

                    const relayKey = topic.split("/").pop(); // Extract relay ID from topic
                    setRelayStatus((prevStatus) => ({
                        ...prevStatus,
                        [relayKey]: payload,
                    }));
                }

                if (topic === TOPIC_HEATER_TEMP) {
                    // console.log("updating time")
                    // const payloadObj = JSON.parse(message.toString());
                    // console.log(payloadObj)
                    try {
                        const payloadObj = JSON.parse(message.toString());

                        // console.log("updating time")

                        // if (payloadObj.temp1 && payloadObj.temp2 && payloadObj.temp3 && payloadObj.temp4) {
                        if (
                            payloadObj.temp1 !== undefined && payloadObj.temp1 !== null &&
                            payloadObj.temp2 !== undefined && payloadObj.temp2 !== null &&
                            payloadObj.temp3 !== undefined && payloadObj.temp3 !== null &&
                            payloadObj.temp4 !== undefined && payloadObj.temp4 !== null
                        ) {

                            lastUpdateRef.current = Date.now(); // ✅ Use ref instead of state

                            console.log("updating time")

                            // ✅ Ensure startTimeRef.current is used, fallback to "0.0"
                            const elapsedSeconds = startTimeRef.current
                                ? ((Date.now() - startTimeRef.current) / 1000).toFixed(2)
                                : "0.0";

                            // // ✅ Check errors for each temperature
                            // const temp1Error = payloadObj.temp1 < 15;
                            // const temp2Error = payloadObj.temp2 < 15;
                            // const temp3Error = payloadObj.temp3 < 15;
                            // const temp4Error = payloadObj.temp4 < 15;

                            const newPoint = {
                                time: parseFloat(elapsedSeconds),
                                timestamp: Date.now(),
                                temp1: payloadObj.temp1 ?? 0,
                                temp2: payloadObj.temp2 ?? 0,
                                temp3: payloadObj.temp3 ?? 0,
                                temp4: payloadObj.temp4 ?? 0,
                                stage: heaterStageRef.current,
                                temp1Error, // ✅ Store temp1 error separately for button disable
                                hasError: payloadObj.temp1 < 15 || payloadObj.temp2 < 15 || payloadObj.temp3 < 15 || payloadObj.temp4 < 15
                            };


                            setHeaterTemp(newPoint);

                            if (isDrawingRef.current) {
                                setChartData((prev) => [...prev, newPoint]);
                            }
                        }
                    } catch (error) {
                        console.error("Error parsing heater temperature data:", error);
                    }
                }

                // Now `payload` is properly defined and can be used
                if (topic === "heater/cmd_raw") {
                    setCmdRawList((prevList) => [payload, ...prevList].slice(0, 10)); // Keep last 10 entries
                } else if (topic === TOPIC_FLOW) {
                    if (typeof payload === "object" && "instantaneous_flow" in payload) {
                        setInstantFlow(payload.instantaneous_flow);
                    } else {
                        console.warn("Unexpected payload format for TOPIC_FLOW:", payload);
                    }
                } else if (topic === TOPIC_USB_STAT) {
                    setRelayStatus(payload);
                } else if (topic.startsWith("usbrelay/state/")) {
                    const relayKey = topic.split("/").pop();
                    setRelayStatus((prevStatus) => ({
                        ...prevStatus,
                        [relayKey]: payload,
                    }));
                } else if (topic === TOPIC_HEATER_STAT) {
                    setHeaterStage(payload);
                }
            });

            client.on("close", () => {
                console.warn("MQTT connection closed.");
            });

            client.on("error", (err) => {
                console.error("MQTT connection error:", err);
            });

            mqttClient.current = client;
        };

        connectToMqtt();

        return () => {
            if (mqttClient.current) mqttClient.current.end();
        };
    }, []);

    const sendHeatCommand = () => {
        if (mqttClient.current) {
            mqttClient.current.publish(TOPIC_HEATER_CMD, "start");
        }
    };

    const sendHeatCommand_stop = (command) => {
        if (mqttClient.current) {
            mqttClient.current.publish("heater/control", command);
            console.log(`Published command: ${command} to heater/control`);
        }
    };

    // Instead of using the first data point's time, compute the minimum time across all data points.
    const minTime = chartData.length > 0 ? Math.min(...chartData.map(point => point.time)) : 0;

    // Create a new array with adjusted time values, ensuring the first point is at exactly 0
    // const adjustedData = chartData.map(point => ({
    //     ...point,
    //     time: point.time - minTime // Exact subtraction without rounding to ensure 0.00
    // }));

    const adjustedData = chartData.map(point => ({
        ...point,
        time: point.time - minTime, // Keep time adjustment
        temp1: (point.temp1 ?? 0) + tempOffset, // Apply offset to all temps
        temp2: (point.temp2 ?? 0) + tempOffset,
        temp3: (point.temp3 ?? 0) + tempOffset,
        temp4: (point.temp4 ?? 0) + tempOffset,
    }));


    const filteredData = useMemo(() => {
        return adjustedData.map((point) => ({
            time: point.time,
            temp1: point.temp1, // Always show H
            temp2: point.temp2, // Always include data but control visibility in Line components
            temp3: point.temp3,
            temp4: point.temp4,
            stage: point.stage,
        }));
    }, [adjustedData, tempOffset]); // Ensure offset is applied dynamically




    return (
        <div className="p-8 font-sans bg-white min-h-screen relative">

            {toastMessage && (
                <div className="fixed bottom-28 left-1/2 transform -translate-x-1/2 bg-green-500 text-white p-3 rounded shadow-lg z-50">
                    {toastMessage}
                    <button
                        className="mt-2 px-4 py-1 bg-gray-800 text-white rounded block mx-auto"
                        onClick={() => setToastMessage("")}
                    >
                        關閉
                    </button>
                </div>

            )}


            {/* Real-time flow value display */}
            <div className="absolute top-4 right-4 bg-white p-4 rounded shadow border w-40 z-10 border-gray-600">
                <h2 className="text-lg font-bold text-blue-900 mb-1">
                    即時氣量
                </h2>

                <div className="relative h-5 w-full bg-gray-200 rounded">
                    <div
                        className="absolute h-full bg-purple-500 rounded"
                        style={{
                            width: `${Math.min((instantFlow / 16) * 100, 100)}%`,
                        }}
                    ></div>
                </div>

                <p className="text-center mt-2 text-sm font-semibold text-gray-700">
                    {(instantFlow ?? 0).toFixed(2)} L/s (
                    {Math.min((instantFlow / 16) * 100, 100).toFixed(1)}%)
                </p>
            </div>

            {/* Wrapper div to arrange both sections side by side */}
            <div className="w-[82%] mx-auto flex gap-1 mt-1 mb-1">
                {/* Temperature Line Chart */}
                <div className="w-[65%] mx-auto p-6 bg-white rounded shadow border border-gray-400">
                    <h2 className="text-2xl font-bold mb-1 text-center">溫度走勢圖</h2>
                    <div>
                        <div className="flex justify-end mb-2">
                            <label className="flex items-center cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={showExtraLines}
                                    onChange={() => setShowExtraLines((prev) => !prev)}
                                    className="hidden"
                                />
                                <div
                                    className={`w-10 h-5 flex items-center rounded-full p-1 duration-300 ease-in-out
                                ${showExtraLines ? "bg-green-500" : "bg-gray-400"}`}
                                >
                                    <div
                                        className={`bg-white w-4 h-4 rounded-full shadow-md transform duration-300 ease-in-out
                                 ${showExtraLines ? "translate-x-5 bg-green-800" : "translate-x-0 bg-gray-700"}`}
                                    ></div>
                                </div>
                                <span className="ml-2 text-gray-700 text-sm">
                                    即時顯示 溫度 M、L、R
                                </span>
                            </label>
                        </div>


                        <ResponsiveContainer width="100%" height={550}>
                            <LineChart data={filteredData}>
                                <CartesianGrid stroke="#ccc" />

                                <XAxis
                                    dataKey="time"
                                    type="number"
                                    domain={[0, Math.ceil(adjustedData[adjustedData.length - 1]?.time || 15)]}
                                    tickCount={Math.ceil(adjustedData[adjustedData.length - 1]?.time || 15) + 1}
                                    interval={0}
                                    allowDecimals={false}
                                    tickFormatter={(tick) => `${tick}s`}
                                    scale="linear"
                                    ticks={Array.from(
                                        { length: Math.ceil(adjustedData[adjustedData.length - 1]?.time || 15) + 1 },
                                        (_, i) => i
                                    )}
                                />

                                <YAxis
                                    domain={[0, 400]}
                                    tick={{ fontSize: 12 }}
                                    tickCount={21}
                                    interval={0}
                                    allowDecimals={false}
                                    ticks={Array.from({ length: 41 }, (_, i) => i * 10)}
                                />

                                <Tooltip
                                    labelFormatter={(label) => `時間: ${label.toFixed(2)} 秒`}
                                    formatter={(value, name, props) => {
                                        const adjustedValue = value + tempOffset; // Apply temperature offset
                                        const stageInfo = props.payload.stage ? `${props.payload.stage}` : "無階段資訊";

                                        // If showExtraLines is false, remove M, L, R entirely
                                        if (!showExtraLines && (name === "溫度 M" || name === "溫度 L" || name === "溫度 R")) {
                                            return [];
                                        }

                                        return [`${adjustedValue.toFixed(1)}°C`, `${name} (${stageInfo})`];
                                    }}
                                    filterNull={true} // Ensures the hidden values don't appear at all
                                    itemSorter={(item) => {
                                        // Completely remove the tooltip title for hidden keys
                                        if (!showExtraLines && (item.name === "溫度 M" || item.name === "溫度 L" || item.name === "溫度 R")) {
                                            return -1; // Forces removal
                                        }
                                        return 1;
                                    }}
                                />



                                <Legend />

                                {/* Always Show Temp H */}
                                <Line type="monotone" dataKey="temp1" stroke="red" strokeWidth={3} dot={false} name="溫度 H" />

                                {/* Show M, L, R dynamically based on the toggle state */}
                                <Line type="monotone" dataKey="temp2" stroke="blue" strokeWidth={1} dot={false} name="溫度 M" strokeOpacity={showExtraLines ? 1 : 0} />
                                <Line type="monotone" dataKey="temp3" stroke="green" strokeWidth={1} dot={false} name="溫度 L" strokeOpacity={showExtraLines ? 1 : 0} />
                                <Line type="monotone" dataKey="temp4" stroke="orange" strokeWidth={1} dot={false} name="溫度 R" strokeOpacity={showExtraLines ? 1 : 0} />
                            </LineChart>
                        </ResponsiveContainer>

                    </div>

                    {drawingCompleted && (
                        <div className="mb-2 text-right"> {/* ✅ Aligns content to the right */}
                            <input
                                type="text"
                                value={filename}
                                onChange={(e) => setFilename(e.target.value)}
                                placeholder="檔名備註(可不填)"
                                className="border border-blue-500 rounded p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />

                            <button
                                onClick={() => saveChartWithTimestamp(chartData, filename)}
                                className="ml-2 px-4 py-2 bg-blue-500 text-white rounded"
                            >
                                儲存圖表
                            </button>
                        </div>
                    )}

                </div>

                {/* Heater Control Section (More Compact) */}
                <div className="w-[35%] bg-gray-100 p-4 rounded shadow-md border border-gray-400">
                    <h2 className="text-xl font-semibold text-center text-blue-900">
                        加熱控制
                    </h2>

                    <div className="flex gap-2">
                        {/* Start Heating Button - Compact */}
                        <button
                            className={`flex-1 px-4 py-2 rounded text-xl  text-white text-base font-medium shadow-md transition-colors 
                            ${isDrawing || drawingCompleted || temp1Error || relayDataStatus !== "繼電器偵測正常" || heaterDataStatus !== "溫度偵測正常"
                                    ? "bg-gray-400 cursor-not-allowed"
                                    : "bg-purple-600 hover:bg-purple-700"}
                        `}
                            onClick={() => sendHeatCommand("start")}
                            disabled={isDrawing || drawingCompleted || temp1Error || relayDataStatus !== "繼電器偵測正常" || heaterDataStatus !== "溫度偵測正常"}
                        >
                            啟動自動測試
                        </button>

                        {/* Stop Heating Button - Smaller Square */}
                        <button
                            className="w-16 h-16 rounded bg-gray-500 text-white text-xl font-medium shadow-md flex items-center justify-center text-center hover:bg-gray-700 transition-colors"
                            onClick={() => sendHeatCommand_stop("stop")}
                        >
                            停止
                        </button>
                    </div>

                    <div className="flex gap-2 mt-2">

                        <div className="absolute top-6 left-2 flex flex-col items-center space-y-2">
                            {/* Heater Status Indicator - Smaller */}
                            <div className="flex flex-col items-center bg-white p-2 rounded-lg shadow-md border border-gray-300 w-32 text-center">
                                <div
                                    className={`w-6 h-6 rounded-full shadow-lg transition-colors duration-500 ${heaterDataStatus === "溫度偵測正常" ? "bg-green-500 slow-flashing" : "bg-red-500 flashing"
                                        }`}
                                ></div>
                                <p className="mt-1 text-sm font-bold text-gray-800 break-words leading-tight">
                                    {heaterDataStatus}
                                </p>
                            </div>

                            {/* Relay Transmission Status Indicator - Smaller */}
                            <div className="flex flex-col items-center bg-white p-2 rounded-lg shadow-md border border-gray-300 w-32 text-center">
                                <div
                                    className={`w-6 h-6 rounded-full shadow-lg transition-colors duration-500 ${relayDataStatus === "繼電器偵測正常" ? "bg-green-500 slow-flashing" : "bg-red-500 flashing"
                                        }`}
                                ></div>
                                <p className="mt-1 text-sm font-bold text-gray-800 break-words leading-tight">
                                    {relayDataStatus}
                                </p>
                            </div>
                        </div>

                        {/* Heating Status & Temperature - Vertical Layout */}
                        <div className="flex flex-col items-center mt-10 gap-2 w-full">

                            {/* Temperature Offset */}

                            <div className="flex items-center bg-white shadow-md border border-gray-300 p-3 rounded-lg w-fit ml-10 space-x-2">
                                <h2 className="text-sm font-semibold text-gray-700 whitespace-nowrap">
                                    溫度補償: {tempOffset}°C
                                </h2>
                                <input
                                    type="number"
                                    value={tempOffset}
                                    onChange={(e) => updateTempOffset(Number(e.target.value))}
                                    className="border border-gray-400 rounded p-1 w-20 text-center text-sm"
                                />
                                <button
                                    onClick={() => {
                                        Cookies.set("TEMP_OFFSET", tempOffset, { expires: 365 });
                                        window.location.reload();
                                    }}
                                    className="px-4 py-1 bg-blue-500 text-white text-xs rounded shadow-md hover:bg-blue-600"
                                >
                                    更新
                                </button>
                            </div>


                            {/* Heating Status */}
                            <div className="bg-white p-4 rounded shadow border border-gray-300 w-5/6 text-center">
                                <h3 className="text-lg font-semibold text-gray-800">測試狀態</h3>
                                <p className="mt-2 text-2xl font-bold text-blue-600">
                                    {heaterStage ? heaterStage : "無加熱狀態資訊"}
                                </p>
                            </div>



                            {/* Heating Temperatures */}
                            <div className="bg-white p-4  mt-1 rounded shadow border border-gray-300 w-5/6 text-center">
                                <h3 className="text-lg font-semibold text-gray-800">加熱溫度</h3>

                                <div className="grid grid-cols-2 gap-2 mt-2">
                                    {[1, 2, 3, 4].map((num) => {
                                        const tempValue = (heaterTemp?.[`temp${num}`] ?? 0) + tempOffset; // Apply offset
                                        const isError = tempValue < 15;

                                        return (
                                            <div key={num} className="flex flex-col items-center text-center bg-gray-100 p-4 rounded shadow-md border border-gray-300 w-35">
                                                <span className="text-md font-semibold text-gray-800">
                                                    溫度 {tempLabels[num]}:
                                                </span>
                                                <span className={`text-xl font-bold mt-1 ${isError ? "text-red-600" : "text-blue-600"}`}>
                                                    {tempValue.toFixed(1)}°C
                                                </span>
                                                {isError && (
                                                    <span className="text-sm text-red-500 font-bold mt-1">
                                                        異常 {num === 1 && "，無法啟動測試"}
                                                    </span>
                                                )}
                                            </div>
                                        );
                                    })}
                                </div>



                            </div>
                        </div>
                    </div>

                    {drawingCompleted && (
                        <h2 className="mt-4 text-lg font-semibold text-center text-red-900">
                            如要重新測試請重新整理頁面
                        </h2>
                    )}
                </div>

            </div>


            <div className="w-1/2 bg-gray-200 mx-auto p-4 rounded-sm border border-gray-400 mt-4">
                <h2 className="text-lg font-semibold mb-1 text-center text-blue-900">
                    繼電器狀態
                </h2>
                <div className="flex justify-between items-center gap-2">
                    {["QAAMZ_3", "QAAMZ_2", "QAAMZ_1"].map((relayKey) => {
                        // Convert the relay status value to a number.
                        // If payload is "1", then Number("1") === 1 and the relay is on.
                        const isOn = Number(relayStatus[relayKey]) === 1;
                        return (
                            <button
                                key={relayKey}
                                className={`flex-1 px-3 py-2 rounded-sm text-white text-sm font-medium ${isOn ? "bg-green-600" : "bg-gray-600"
                                    }`}
                                disabled
                            >
                                {relayNames[relayKey]} ({relayKey})： {isOn ? "開啟" : "關閉"}
                            </button>
                        );
                    })}
                </div>
            </div>

        </div>
    );
};

export default MqttPage;
