import React, { useEffect, useState, useRef } from "react";
import mqtt from "mqtt";
import ReactECharts from "echarts-for-react";
import config from "./config";
import { calculateRelayStats } from "./calculateRelayStats";
import Cookies from "js-cookie";
import html2canvas from "html2canvas"; // Import html2canvas

const { mqttHost, mqttUsername, mqttPassword } = config;

const getInitialThreshold = () => {
    const storedThreshold = Cookies.get("THRESHOLD");
    return storedThreshold ? parseInt(storedThreshold, 10) || 50 : 50; // Default 50
};

const MqttPage = () => {
    // Various state variables and refs
    const testStartTimeRef = useRef(null);
    const [currentProject, setCurrentProject] = useState(null);
    const [isStarted, setIsStarted] = useState(false);
    const [savedProjects, setSavedProjects] = useState([]);
    const [instantFlow, setInstantFlow] = useState(0);
    const [relayStatus, setRelayStatus] = useState({});
    const mqttClient = useRef(null);
    const [activeRelay, setActiveRelay] = useState(null);
    const activeRelayRef = useRef(null);
    const [hoveredProject, setHoveredProject] = useState(null);
    const [tooltipStyle, setTooltipStyle] = useState({});
    const [flowData, setFlowData] = useState([]); // Store flow data for chart
    const [TestStage, setTestStage] = useState(""); // Test stage value
    const [isDrawing, setIsDrawing] = useState(false);
    const autoProcessRunningRef = useRef(false);
    const lastFlowUpdateRef = useRef(Date.now());
    const lastRelayUpdateRef = useRef(Date.now());

    // Modal state for upload feedback using toast CSS
    const [toastMessage, setToastMessage] = useState("");

    // Refs for components:
    const chartRef = useRef(null);
    // New ref that wraps both the chart and saved projects sections
    const captureAreaRef = useRef(null);
    const [drawtestCompleted, setDrawTestCompleted] = useState(false);



    const [flowDataStatus, setFlowDataStatus] = useState("氣體偵測正常"); // Default: Normal
    const [relayDataStatus, setRelayDataStatus] = useState("繼電器偵測正常"); // Default: Normal

    const flowDataRef = useRef([]);
    const [threshold, setThreshold] = useState(getInitialThreshold());
    const testCompletedRef = useRef(false);
    // Create a dummy state that you can update to force re-render
    // const [_, forceUpdate] = useState(0);




    useEffect(() => {
        console.log("Threshold updated:", threshold);
        Cookies.set("THRESHOLD", threshold, { expires: 365 });
    }, [threshold]);

    const updateThreshold = (newThreshold) => {
        if (!isNaN(newThreshold) && newThreshold > 0) {
            setThreshold(newThreshold);
        }
    };

    useEffect(() => {
        flowDataRef.current = flowData;
    }, [flowData]);

    const TOPIC_FLOW = "air/flow"; // Flow topic

    const [autoProcessRunning, setAutoProcessRunning] = useState(false);
    useEffect(() => {
        flowDataRef.current = flowData;
    }, [flowData]);

    // Helper delay function
    const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

    const handleMouseEnter = (event, project) => {
        console.log("Hovered Project Data:", project);
        setHoveredProject(project);
        const tooltipWidth = 300;
        const tooltipHeight = 150;
        const { clientX, clientY } = event;
        let left = clientX + 20;
        let top = clientY + 20;
        if (left + tooltipWidth > window.innerWidth) {
            left = window.innerWidth - tooltipWidth - 10;
        }
        if (top + tooltipHeight > window.innerHeight) {
            top = window.innerHeight - tooltipHeight - 10;
        }
        setTooltipStyle({ left, top });
    };

    const handleMouseLeave = () => {
        setHoveredProject(null);
        setTooltipStyle({});
    };

    const isStartedRef = useRef(isStarted);
    const currentProjectRef = useRef(currentProject);

    useEffect(() => {
        const active = Object.keys(relayStatus).find(
            (key) => relayStatus[key] === "ON"
        );
        setActiveRelay(active || null);
    }, [relayStatus]);

    useEffect(() => {
        activeRelayRef.current = activeRelay;
    }, [activeRelay]);

    useEffect(() => {
        if (currentProject) {
            setCurrentProject((prevProject) => ({
                ...prevProject,
                color: getDarkColor(activeRelay),
            }));
        }
    }, [activeRelay]);

    useEffect(() => {
        isStartedRef.current = isStarted;
    }, [isStarted]);

    useEffect(() => {
        currentProjectRef.current = currentProject;
    }, [currentProject]);

    const relayColors = {
        "1": "#0000FF", // Blue for QAAMZ_1
        "2": "#008000", // Green for QAAMZ_2
        "3": "#FF0000", // Red for QAAMZ_3
    };

    const getDarkColor = (relay) => {
        return relayColors[relay] || "#2F4F4F";
    };

    useEffect(() => {
        autoProcessRunningRef.current = autoProcessRunning;
    }, [autoProcessRunning]);

    useEffect(() => {
        const timer = setInterval(() => {
            const now = Date.now();
            const timeSinceLastFlowUpdate = now - lastFlowUpdateRef.current;
            const timeSinceLastRelayUpdate = now - lastRelayUpdateRef.current;
            if (timeSinceLastFlowUpdate > 1500) {
                setFlowDataStatus("氣體傳輸錯誤\\請檢查USB連線\n無法測試");
            } else {
                setFlowDataStatus("氣體偵測正常");
            }
            if (timeSinceLastRelayUpdate > 1500) {
                setRelayDataStatus("繼電器傳輸錯誤\n請檢查USB連線\n無法測試");
            } else {
                setRelayDataStatus("繼電器偵測正常");
            }
        }, 1000);
        return () => clearInterval(timer);
    }, []);

    // MQTT connection
    useEffect(() => {
        const connectToMqtt = () => {
            mqttClient.current = mqtt.connect(mqttHost, {
                username: mqttUsername,
                password: mqttPassword,
                reconnectPeriod: 1000,
            });

            mqttClient.current.on("connect", () => {
                console.log("Connected to MQTT broker");
                mqttClient.current.subscribe(
                    [
                        "usbrelay/state/QAAMZ_1",
                        "usbrelay/state/QAAMZ_2",
                        "usbrelay/state/QAAMZ_3",
                        TOPIC_FLOW,
                        "autotest/flow1/stage",
                    ],
                    (err) => {
                        if (err) {
                            console.error("Subscription error:", err);
                        }
                    }
                );
            });

            mqttClient.current.on("message", (topic, message) => {
                const payload = message.toString();
                let relayKey = null;
                if (topic === "usbrelay/state/QAAMZ_1") {
                    relayKey = "1";
                } else if (topic === "usbrelay/state/QAAMZ_2") {
                    relayKey = "2";
                } else if (topic === "usbrelay/state/QAAMZ_3") {
                    relayKey = "3";
                }
                if (relayKey !== null) {
                    setRelayStatus((prevStatus) => ({
                        ...prevStatus,
                        [relayKey]: payload === "1" ? "ON" : "OFF",
                    }));
                }
                if (topic === "autotest/flow1/stage") {
                    console.log(`Received Test Stage: ${payload}`);
                    setTestStage(payload);
                    if (payload === "測試開始: 全部關閉") {
                        testStartTimeRef.current = Date.now();
                        setIsDrawing(true);
                        setFlowData([]);
                        flowDataRef.current = [];
                        setAutoProcessRunning(true);
                        autoProcessRunningRef.current = true;
                    } else if (payload === "測試結束: 全部關閉") {
                        setIsDrawing(false);
                        setAutoProcessRunning(false);
                        autoProcessRunningRef.current = false;
                        testCompletedRef.current = true;
                        // Force update to re-render the component
                        // forceUpdate(n => n + 1);
                        setDrawTestCompleted(true); // update state
                        const timestamp = new Date().toLocaleString("zh-TW", {
                            year: "numeric",
                            month: "2-digit",
                            day: "2-digit",
                            hour: "2-digit",
                            minute: "2-digit",
                            second: "2-digit",
                            hour12: false,
                        });
                        console.log("Flow Data before stats calculation:", flowDataRef.current);
                        const statsResult = calculateRelayStats(flowDataRef.current, 15, threshold);
                        console.log("Stats result:", statsResult);
                        const newProject = {
                            name: `測試 ${timestamp}`,
                            數據量: flowDataRef.current.length,
                            baseMean: statsResult.baseMean,
                            meanValues: statsResult.meanValues,
                            percentages: statsResult.relayPercentages,
                            needChange: statsResult.needChange,
                            threshold: threshold,
                            flowData: flowDataRef.current,
                        };
                        setSavedProjects((prev) => [newProject, ...prev]);
                        console.log("Project Saved:", newProject);
                        console.log(JSON.stringify(newProject, null, 2));
                    }
                }
                if (topic.startsWith("usbrelay/state/")) {
                    lastRelayUpdateRef.current = Date.now();
                }
                if (topic === TOPIC_FLOW) {
                    try {
                        const payloadObj = JSON.parse(payload);
                        if (payloadObj.hasOwnProperty("instantaneous_flow")) {
                            const newFlowValue = payloadObj.instantaneous_flow;
                            const relayKey = activeRelayRef.current;
                            setInstantFlow(newFlowValue);
                            lastFlowUpdateRef.current = Date.now();
                            if (autoProcessRunningRef.current && relayKey) {
                                setFlowData((prevData) => {
                                    const now = Date.now();
                                    const elapsedSec = testStartTimeRef.current
                                        ? ((now - testStartTimeRef.current) / 1000)
                                        : 0;
                                    const elapsedStr = parseFloat(elapsedSec).toFixed(2);
                                    const updatedData = [...prevData];
                                    const existingIndex = updatedData.findIndex(
                                        (point) => point.time === elapsedStr && point.relay === relayKey
                                    );
                                    if (existingIndex !== -1) {
                                        updatedData[existingIndex].value = newFlowValue;
                                    } else {
                                        updatedData.push({ time: elapsedStr, value: newFlowValue, relay: relayKey });
                                    }
                                    return updatedData;
                                });
                            }
                        }
                    } catch (error) {
                        console.error("Error parsing flow data:", error);
                    }
                }
            });

            mqttClient.current.on("close", () => {
                console.warn("MQTT connection closed.");
            });

            mqttClient.current.on("error", (err) => {
                console.error("MQTT connection error:", err);
            });
        };

        connectToMqtt();
        return () => {
            if (mqttClient.current) {
                mqttClient.current.end();
            }
        };
    }, []);

    const sendRelayCommand = async (relayOrTopic, command) => {
        if (!mqttClient.current || !mqttClient.current.connected) {
            console.warn("MQTT not connected, waiting to publish...");
            let attempts = 0;
            while ((!mqttClient.current || !mqttClient.current.connected) && attempts < 10) {
                await delay(500);
                attempts++;
            }
            if (!mqttClient.current || !mqttClient.current.connected) {
                console.error("MQTT still not connected, cannot send command");
                return;
            }
        }
        const topic =
            typeof relayOrTopic === "string" && relayOrTopic.includes("all")
                ? relayOrTopic
                : `usbrelay/control/QAAMZ_${relayOrTopic}`;
        mqttClient.current.publish(topic, command, {}, (err) => {
            if (err) {
                console.error("Failed to send relay command:", err);
            } else {
                console.log(`Command sent to ${topic}: ${command}`);
            }
        });
    };

    const handleRelayToggle = (relay) => {
        sendRelayCommand(relay, "toggle");
    };

    const autoProcess1 = async () => {
        try {
            if (mqttClient.current) {
                mqttClient.current.publish("autotest/flow1", "start");
                console.log("Published 'start' to autotest/flow1");
            }
        } catch (error) {
            console.error("Error during auto process 1:", error);
        }
    };

    // Calculate the minimum time value to shift all points to start at 0
    const minTime = flowData.length > 0 ? Math.min(...flowData.map(point => parseFloat(point.time))) : 0;

    // Get all unique relays in the data
    const uniqueRelays = [...new Set(flowData.map(point => point.relay))];

    // Prepare series data for each relay
    const seriesData = {};
    const relayMapping = { "1": "右側", "2": "全開", "3": "左側" };
    const orderedRelays = ["3", "2", "1"]; // Display in this order

    // Process each relay separately
    uniqueRelays.forEach(relay => {
        // Get points for this relay and sort by time
        const relayPoints = flowData
            .filter(point => point.relay === relay)
            .sort((a, b) => parseFloat(a.time) - parseFloat(b.time));

        // Initialize the series data array for this relay
        seriesData[relay] = [];

        if (relayPoints.length > 0) {
            // For each relay, add its points with time adjusted to start at 0
            relayPoints.forEach((point, index) => {
                // If this is the first point, set its value to 0
                const value = index === 0 ? 0 : parseFloat(point.value);

                seriesData[relay].push([
                    parseFloat(point.time) - minTime,
                    value
                ]);
            });
        }
    });

    const chartOptions = {
        title: {
            text: "即時流量變化圖",
        },
        legend: {
            data: orderedRelays.map(
                (relayKey) => `Relay ${relayKey} (${relayMapping[relayKey]})`
            ),
            top: 20,
        },
        tooltip: {
            trigger: "axis",
        },
        xAxis: {
            type: "value",
            min: 0,
            interval: 1,
            name: "秒數",
        },
        yAxis: {
            type: "value",
            name: "流量 (L/s)",
        },
        series: orderedRelays.map((relayKey) => ({
            name: `Relay ${relayKey} (${relayMapping[relayKey]})`,
            type: "line",
            data: seriesData[relayKey],
            smooth: true,
            symbol: "circle",
            itemStyle: {
                color: relayColors[relayKey],
            },
            lineStyle: {
                width: 3,
                color: relayColors[relayKey],
            },
        })),
    };

    // New capture function that uses captureAreaRef to capture both chart and saved projects sections.
    function saveChartWithTimestamp(chartData, filename) {
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

        const filenameSuffix = filename ? `_${filename}` : "";
        const baseFilename = `${taiwanTime}${filenameSuffix}`;

        // Use the captureAreaRef instead of chartRef.
        const captureElement = captureAreaRef.current;
        if (!captureElement) {
            console.error("❌ Capture area element not found");
            return;
        }

        console.log("✅ Capturing image of chart and saved projects...");
        html2canvas(captureElement, { scale: 2 })
            .then((canvas) => {
                canvas.toBlob((blob) => {
                    if (!blob) {
                        console.error("❌ Blob creation failed");
                        setToastMessage(
                            <p className="text-center text-red-600">截圖失敗：無法創建圖像Blob</p>
                        );
                        return;
                    }
                    const jsonBlob = new Blob([JSON.stringify(chartData, null, 2)], {
                        type: "application/json",
                    });
                    const formData = new FormData();
                    formData.append("file", blob, `${baseFilename}.png`);
                    formData.append("json_file", jsonBlob, `${baseFilename}.json`);
                    formData.append("project", "airflow");

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
                            console.log("✅ 上傳成功:", data);
                            const imageFilename =
                                data.image_filename || `${baseFilename}.png`;
                            const jsonFilename =
                                data.json_filename || `${baseFilename}.json`;
                            setToastMessage(
                                <div className="text-center">
                                    <p>📤 圖片與圖表數據上傳成功！</p>
                                    <p className="text-xs mt-1 text-left">
                                        檔案夾: <span className="font-mono">airflow</span>
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
                                    上傳失敗: {error.message}
                                </p>
                            );
                        });
                }, "image/png");
            })
            .catch((error) => {
                console.error("❌ Error capturing image:", error);
                setToastMessage(
                    <p className="text-center text-red-600">截圖失敗: {error.message}</p>
                );
            });
    }

    console.log(drawtestCompleted);

    return (
        <div className="p-8 font-sans bg-white min-h-screen relative">
            <div className="flex items-stretch justify-between space-x-4">
                {/* Status Indicator */}
                <div className="absolute top-1 left-14 flex items-center space-x-6">
                    <div className="flex flex-col items-center bg-white p-3 rounded-lg shadow-md border border-gray-300 w-30 text-center">
                        <div
                            className={`w-8 h-8 rounded-full shadow-md transition-colors duration-500 ${flowDataStatus === "氣體偵測正常"
                                ? "bg-green-500 slow-flashing"
                                : "bg-red-500 flashing"
                                }`}
                        ></div>
                        <p className="mt-2 text-sm font-bold text-gray-800 break-words leading-tight whitespace-pre-wrap">
                            {flowDataStatus}
                        </p>
                    </div>
                    <div className="flex flex-col items-center bg-white p-3 rounded-lg shadow-md border border-gray-300 w-33 text-center">
                        <div
                            className={`w-8 h-8 rounded-full shadow-md transition-colors duration-500 ${relayDataStatus === "繼電器偵測正常"
                                ? "bg-green-500 slow-flashing"
                                : "bg-red-500 flashing"
                                }`}
                        ></div>
                        <p className="mt-2 text-sm font-bold text-gray-800 break-words leading-tight whitespace-pre-wrap">
                            {relayDataStatus}
                        </p>
                    </div>
                    {/* Threshold Adjustment */}
                    <div className="flex flex-col items-center bg-white shadow-md border border-gray-300 p-3 rounded-lg w-28 ml-10">
                        <h2 className="text-sm font-semibold text-gray-700">
                            更換 %: {threshold}
                        </h2>
                        <input
                            type="number"
                            value={threshold}
                            onChange={(e) => updateThreshold(Number(e.target.value))}
                            className="border border-gray-400 rounded p-1 w-20 text-center text-sm"
                        />
                        <button
                            onClick={() => {
                                Cookies.set("THRESHOLD", threshold, { expires: 365 });
                                window.location.reload();
                            }}
                            className="mt-1 px-4 py-1 bg-blue-500 text-white text-xs rounded shadow-md hover:bg-blue-600"
                        >
                            更新
                        </button>
                    </div>
                    {/* Flashing animation styles */}
                    <style>
                        {`
              @keyframes flashing {
                0%, 100% { opacity: 1; }
                50% { opacity: 0; }
              }
              .flashing {
                animation: flashing 1s infinite;
              }
              .slow-flashing {
                animation: flashing 3s infinite;
              }
            `}
                    </style>
                </div>

                {/* Relay Control Section */}
                <div className="w-1/3 mt-20 bg-gray-200 p-6 rounded shadow-md border border-gray-400 h-36">
                    <h2 className="text-lg font-semibold mb-4 text-center text-blue-900">
                        手動繼電器控制
                    </h2>
                    <div className="flex justify-between items-center gap-4">
                        {[3, 2, 1].map((relay) => (
                            <label key={relay} className="flex items-center cursor-pointer">
                                <div className="relative">
                                    <input
                                        type="checkbox"
                                        disabled={
                                            autoProcessRunning ||
                                            testCompletedRef.current ||
                                            relayDataStatus !== "繼電器偵測正常" ||
                                            flowDataStatus !== "氣體偵測正常"
                                        }
                                        checked={relayStatus[relay] === "ON"}
                                        onChange={() => handleRelayToggle(relay)}
                                        className="sr-only"
                                    />
                                    <div
                                        className={`block w-14 h-8 rounded-full ${relayStatus[relay] === "ON"
                                            ? "bg-green-600"
                                            : "bg-gray-600"
                                            }`}
                                    ></div>
                                    <div
                                        className={`dot absolute left-1 top-1 bg-white w-6 h-6 rounded-full transition-transform ${relayStatus[relay] === "ON" ? "translate-x-full" : ""
                                            }`}
                                    ></div>
                                </div>
                                <span className="ml-3 text-gray-700">
                                    {relay === 2 ? "全開(2)" : relay === 3 ? "左側(3)" : "右側(1)"}
                                </span>
                            </label>
                        ))}
                    </div>
                </div>

                {/* Auto Test Section */}
                <div className="w-1/3 bg-gray-200 p-6 rounded shadow-md border border-gray-400 h-56 flex flex-col justify-between">
                    <h2 className="text-lg font-semibold text-center text-blue-900">
                        自動測試
                    </h2>
                    <div className="flex flex-col items-center">
                        <p className="text-green-700 text-xl font-bold bg-green-200 px-4 py-2 rounded-lg shadow-md">
                            {TestStage || "未開始"}
                        </p>
                    </div>
                    <div className="flex justify-center">
                        {testCompletedRef.current ? (
                            <span className="text-red-900 font-bold">
                                如要重新測試請重新整理頁面
                            </span>
                        ) : (
                            <button
                                disabled={
                                    autoProcessRunning ||
                                    relayDataStatus !== "繼電器偵測正常" ||
                                    flowDataStatus !== "氣體偵測正常"
                                }
                                className="px-6 py-3 rounded text-white text-lg font-medium shadow-md transition bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                                onClick={autoProcess1}
                            >
                                自動流程1
                            </button>
                        )}
                    </div>
                </div>

                {/* Real-Time Air Section */}
                <div className="w-1/3 bg-white p-8 rounded shadow border border-gray-600 h-36">
                    <h2 className="text-lg font-bold text-gray-700 mb-1 text-blue-900">
                        即時氣量
                    </h2>
                    <div className="relative h-8 w-full bg-gray-200 rounded">
                        <div
                            className="absolute h-full bg-purple-500 rounded"
                            style={{
                                width: `${Math.min((instantFlow / 16) * 100, 100)}%`,
                            }}
                        ></div>
                    </div>
                    <p className="text-center mt-4 text-lg font-semibold text-gray-700">
                        {instantFlow.toFixed(2)} L/s (
                        {Math.min((instantFlow / 16) * 100, 100).toFixed(1)}%)
                    </p>
                </div>
            </div>

            {/* Capture Area: Chart Section + Saved Projects Section */}
            <div ref={captureAreaRef}>
                {/* Chart Section */}
                <div className="mt-2">
                    <ReactECharts
                        ref={chartRef}
                        option={chartOptions}
                        style={{ height: "400px", width: "100%" }}
                    />
                </div>
                {/* Saved Projects Section */}
                <div className="p-8 font-sans bg-gray-200 min-h-[100px] relative">
                    {savedProjects.length > 0 ? (
                        <div
                            onMouseEnter={(event) => handleMouseEnter(event, savedProjects[0])}
                            onMouseLeave={handleMouseLeave}
                            className="relative cursor-pointer"
                            dangerouslySetInnerHTML={{
                                __html: (() => {
                                    const project = savedProjects[0];
                                    const relayOrder = ["3", "2", "1"];
                                    const relayMapping = {
                                        "3": "左邊",
                                        "2": "全開",
                                        "1": "右側",
                                    };
                                    const meanString = project.meanValues
                                        ? Object.entries(project.meanValues)
                                            .filter(([relay]) => relayOrder.includes(relay))
                                            .sort(
                                                ([a], [b]) =>
                                                    relayOrder.indexOf(a) - relayOrder.indexOf(b)
                                            )
                                            .map(([relay, value]) => {
                                                const percentage = project.percentages?.[relay] ?? "N/A";
                                                const valueDisplay =
                                                    value === null ? "Insufficient Data" : value.toFixed(2);
                                                return `<span>${relay} (${relayMapping[relay]}):</span>
                          <span class="text-orange-800 font-bold text-2xl">${valueDisplay}</span>
                          <span class="text-gray-600 text-sm"> (${percentage})</span>`;
                                            })
                                            .join(
                                                `<span style="display: inline-block; margin: 0 20px; font-size: 1.5em;">/</span>`
                                            )
                                        : "No data";
                                    const warningMessage = project.needChange
                                        ? `<span class="text-blue-600 text-2xl ml-4">有一孔以上阻塞超過${project.threshold}%, 建議更換</span>`
                                        : "";
                                    return `${project.name}（數據量: ${project.數據量}） 
                  <span class="ml-2 text-gray-500">${meanString}</span>
                  ${warningMessage}`;
                                })(),
                            }}
                        ></div>
                    ) : (
                        <p>目前沒有測試結果</p>
                    )}
                </div>
            </div>

            {/* Button to trigger capture/upload */}
            {drawtestCompleted && (
                <div className="mt-4 text-center">
                    <input
                        type="text"
                        placeholder="檔名備註"
                        onChange={(e) => {
                            // Optionally store filename in state if needed
                        }}
                        className="border p-2 rounded"
                    />
                    <button
                        onClick={() => saveChartWithTimestamp(flowData, "note")}
                        className="ml-2 px-4 py-2 bg-blue-500 text-white rounded"
                    >
                        儲存圖表
                    </button>
                </div>
            )}

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

        </div>
    );
};

export default MqttPage;
