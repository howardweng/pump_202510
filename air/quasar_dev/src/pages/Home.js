import React, { useEffect, useState, useRef } from "react";
import mqtt from "mqtt";
import ReactECharts from "echarts-for-react";

const MqttPage = () => {
    const [currentProject, setCurrentProject] = useState(null); // Current project object
    const [isStarted, setIsStarted] = useState(false); // State to control timeline start/stop
    const [savedProjects, setSavedProjects] = useState([]); // Array to store completed projects
    const [instantFlow, setInstantFlow] = useState(0); // Real-time instant flow value
    const [relayStatus, setRelayStatus] = useState({}); // Relay statuses
    const mqttClient = useRef(null); // Persistent MQTT client
    const updateThrottle = useRef(false); // Throttle to limit updates
    // const mqttHost = "ws://localhost:9500";
    const mqttHost = "ws://192.168.1.102:9500";
    const TOPIC_FLOW = "air/flow";
    const TOPIC_STAT = "usbrelay/stat"; // Topic for relay statuses
    const TOPIC_CMD = "usbrelay/cmd"; // Topic for relay commands
    const [activeRelay, setActiveRelay] = useState(null); // Track the active relay
    const activeRelayRef = useRef(null);

    const [hoveredProject, setHoveredProject] = useState(null);
    const [tooltipStyle, setTooltipStyle] = useState({}); // State to track tooltip position

    // Define baseValues as a component parameter
    const baseValues = {
        "3": 7.5,  // Left side
        "2": 16.0, // Full open
        "1": 5.8   // Right side
    };


    const handleMouseEnter = (event, project) => {
        setHoveredProject(project);

        // Calculate tooltip position dynamically
        const tooltipWidth = 300; // Approximate tooltip width
        const tooltipHeight = 100; // Approximate tooltip height
        const { clientX, clientY } = event;

        let left = clientX + 20; // Add some padding to the right of the mouse
        let top = clientY + 20; // Add some padding below the mouse cursor

        // Adjust position if tooltip goes beyond viewport
        if (left + tooltipWidth > window.innerWidth) {
            left = window.innerWidth - tooltipWidth - 10; // Ensure tooltip doesn't overflow horizontally
        }
        if (top + tooltipHeight > window.innerHeight) {
            top = window.innerHeight - tooltipHeight - 10; // Ensure tooltip doesn't overflow vertically
        }

        setTooltipStyle({ left, top });
    };

    const handleMouseLeave = () => {
        setHoveredProject(null); // Clear the hovered project
        setTooltipStyle({}); // Reset tooltip position
    };



    const isStartedRef = useRef(isStarted);
    const currentProjectRef = useRef(currentProject);

    useEffect(() => {
        const active = Object.keys(relayStatus).find((key) => relayStatus[key] === "ON");
        setActiveRelay(active || null);
        // console.log("get value of activeRelay:", activeRelay); // Logs after state updates
    }, [relayStatus]);


    useEffect(() => {
        activeRelayRef.current = activeRelay;
        // console.log("Updated activeRelay:", activeRelay); // Logs after state updates
    }, [activeRelay]);

    useEffect(() => {
        if (currentProject) {
            setCurrentProject((prevProject) => ({
                ...prevProject,
                color: getDarkColor(activeRelay), // Update color dynamically
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
        2: "#008000", // Dark Green
        3: "#FF0000", // Regular Red
        1: "#0000FF", // Regular Blue
    };



    const getDarkColor = (relay) => {
        return relayColors[relay] || "#2F4F4F"; // Default color (Dark Gray) if relay not found
    };





    useEffect(() => {
        // Function to connect to MQTT broker
        const connectToMqtt = () => {
            mqttClient.current = mqtt.connect(mqttHost);

            mqttClient.current.on("connect", () => {
                console.log("Connected to MQTT broker");
                mqttClient.current.subscribe([TOPIC_FLOW, TOPIC_STAT], (err) => {
                    if (err) {
                        console.error("Subscription error:", err);
                    }
                });
            });

            mqttClient.current.on("message", (topic, message) => {
                const payload = JSON.parse(message.toString());
                if (topic === TOPIC_FLOW) {
                    setInstantFlow(payload.instant); // Update real-time flow value

                    if (isStartedRef.current && currentProjectRef.current) {
                        if (!updateThrottle.current) {
                            const now = new Date().getTime();
                            const elapsedTime = now - currentProjectRef.current.startTime;

                            // Format time as `SS:MM`
                            const seconds = Math.floor((elapsedTime / 1000) % 60).toString().padStart(2, "0");
                            const milliseconds = Math.floor((elapsedTime % 1000) / 10).toString().padStart(2, "0");
                            const timestamp = `${seconds}:${milliseconds}`;



                            // console.log('####activeRelay', activeRelayRef)


                            setCurrentProject((prevProject) => {
                                if (!prevProject) return null;

                                const updatedProject = {
                                    ...prevProject,
                                    data: [
                                        ...prevProject.data,
                                        {
                                            time: timestamp,
                                            value: payload.instant,
                                            relay: activeRelayRef.current || "unknown", // Use ref for the latest value
                                        },
                                    ],
                                    數據量: prevProject.數據量 + 1,
                                };

                                console.log("Updated project data:", updatedProject.data);
                                return updatedProject;
                            });





                            updateThrottle.current = true;
                            setTimeout(() => {
                                updateThrottle.current = false;
                            }, 100); // Throttle updates to every 0.1 seconds
                        }
                    }
                } else if (topic === TOPIC_STAT) {
                    setRelayStatus(payload); // Update relay statuses
                }
            });

            mqttClient.current.on("close", () => {
                console.log("MQTT connection closed. Attempting to reconnect...");
                connectToMqtt(); // Reconnect when connection is lost
            });

            mqttClient.current.on("error", (err) => {
                console.error("MQTT connection error:", err);
            });
        };

        // Connect to MQTT broker
        connectToMqtt();

        return () => {
            if (mqttClient.current) {
                mqttClient.current.end();
            }
            // setActiveRelay(null); // Reset active relay on unmount
        };

    }, []); // Only runs once




    const sendRelayCommand = (command) => {
        mqttClient.current.publish(TOPIC_CMD, JSON.stringify(command), {}, (err) => {
            if (err) {
                console.error("Failed to send relay command:", err);
            } else {
                console.log("Relay command sent:", command);
            }
        });
    };

    const handleProjectControl = (isStart) => {
        if (isStart) {
            const now = new Date();
            const formatter = new Intl.DateTimeFormat("zh-TW", {
                timeZone: "Asia/Taipei",
                year: "numeric",
                month: "2-digit",
                day: "2-digit",
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
                hour12: false,
            });

            const parts = formatter.formatToParts(now);
            const year = parts.find((part) => part.type === "year").value;
            const month = parts.find((part) => part.type === "month").value;
            const day = parts.find((part) => part.type === "day").value;
            const hour = parts.find((part) => part.type === "hour").value;
            const minute = parts.find((part) => part.type === "minute").value;
            const second = parts.find((part) => part.type === "second").value;

            const projectName = `AIR${year}${month}${day}_${hour}${minute}${second}`;

            setCurrentProject({
                name: projectName,
                color: getDarkColor(activeRelayRef.current),
                data: [],
                數據量: 0,
                startTime: now,
                baseValues, // Include baseValues in the project data
            });

        } else {
            setSavedProjects((prevSaved) => {
                if (currentProject) {
                    // Calculate the stable mean and percentages
                    const mean = calculateStableMean(currentProject.data);
                    const percentages = {};
                    let hasLowPerformance = false;

                    // Calculate percentages and check performance using project's baseValues
                    Object.entries(mean).forEach(([relay, data]) => {
                        if (currentProject.baseValues[relay]) {
                            const value = parseFloat(data.value);
                            const percentage = ((value / currentProject.baseValues[relay]) * 100).toFixed(1);
                            percentages[relay] = percentage;
                            if (percentage < 50) {
                                hasLowPerformance = true;
                            }
                        }
                    });

                    // Attach all calculated data to the project
                    const updatedProject = {
                        ...currentProject,
                        mean,
                        percentages,
                        hasLowPerformance,
                    };

                    const updatedSavedProjects = [...prevSaved, updatedProject];
                    console.log("Saved Projects JSON:", JSON.stringify(updatedSavedProjects, null, 2));
                    return updatedSavedProjects;
                }
                return prevSaved;
            });

            setCurrentProject(null);
        }

        setIsStarted(isStart);
    };


    const relayNames = {
        2: "全開", // Full Open
        3: "左側", // Left Side
        1: "右側", // Right Side
    };

    const calculateStableMean = (data) => {
        const relayGroups = {};
        let lastRelay = null;
        let countForRelay = 0;

        data.forEach((point) => {
            const { relay, value } = point;

            if (!relayGroups[relay]) {
                relayGroups[relay] = [];
                countForRelay = 0; // Reset count for a new relay
            }

            if (relay !== lastRelay) {
                // New relay detected
                countForRelay = 0; // Reset the count on relay change
            }

            if (countForRelay >= 4) {
                // Only add data points after the first two for the current relay
                relayGroups[relay].push(value);
            }

            countForRelay++;
            lastRelay = relay;
        });

        // Calculate the stable mean for each relay
        const stableMean = {};
        Object.keys(relayGroups).forEach((relay) => {
            const values = relayGroups[relay];
            if (values.length > 0) {
                // Only consider non-zero, stable values
                const stableValues = values.filter((value) => value !== null && value !== 0);
                const mean =
                    stableValues.reduce((sum, value) => sum + value, 0) /
                    stableValues.length;
                stableMean[relay] = {
                    name: relayNames[relay] || "未知", // Relay name or "Unknown"
                    value: mean.toFixed(2), // Keep two decimal places
                };
            } else {
                stableMean[relay] = {
                    name: relayNames[relay] || "未知", // Relay name or "Unknown"
                    value: "No Data",
                };
            }
        });

        return stableMean;
    };




    const handleRelayToggle = (relay) => {
        const command = {};
        const relayKey = String(relay); // Ensure relay is treated as a string

        // Toggle the relay state
        if (relayStatus[relayKey] === "ON") {
            command[relayKey] = "OFF";
            console.log(`Turning OFF relay: ${relay}`); // Debug log

            // Check if all relays are off
            const allOff = Object.keys(relayStatus).every(
                (key) => key === relayKey || relayStatus[key] === "OFF"
            );
            if (allOff) {
                console.log("All relays OFF. Stopping project."); // Debug log
                // setActiveRelay(null); // No active relay
                handleProjectControl(false); // Stop the project
            }
        } else {
            command[relayKey] = "ON";
            console.log(`Turning ON relay: ${relay}`); // Debug log

            // Only one relay can be active at a time
            Object.keys(relayStatus).forEach((key) => {
                command[key] = key === relayKey ? "ON" : "OFF";
            });


            console.log('updating relay', relay)
            // Set active relay to the currently toggled relay
            // setActiveRelay(relay);
            console.log(`Active relay set to: ${relay}`); // Debug log

            if (!isStarted) {
                console.log("Starting project as relay is turned ON."); // Debug log
                handleProjectControl(true);
            }
        }

        // Send only the changed relay command
        console.log("Command to send:", command); // Debug log
        sendRelayCommand(command);

        // Update relay status locally for instant feedback
        setRelayStatus((prevStatus) => {
            const updatedStatus = { ...prevStatus, [String(relay)]: command[relay] };
            console.log("Updated relay status:", updatedStatus); // Debug log
            return updatedStatus;
        });

    };




    const chartOptions = {
        title: {
            text: "即時流量儀表板",
        },
        tooltip: {
            trigger: "axis",
            formatter: (params) =>
                params
                    .map(
                        (param) =>
                            `<strong>${param.seriesName} - ${relayNames[param.data.relay] || '未知'}</strong><br/>時間: ${param.data.name}<br/>數值: ${param.data.value ?? "無"}`
                    )
                    .join("<br/>"),
        },
        xAxis: {
            type: "category",
            name: "時間戳",
        },
        yAxis: {
            type: "value",
            name: "瞬時流量 (L/s)",
        },
        series: (() => {
            if (!currentProject) return [];

            // Collect all timestamps with data for each relay
            const relayDataMap = {};
            currentProject.data.forEach((point) => {
                if (!relayDataMap[point.relay]) {
                    relayDataMap[point.relay] = [];
                }
                relayDataMap[point.relay].push(point);
            });

            let lastRelay = null;
            let lastValue = null;

            return Object.keys(relayColors).map((relay) => {
                const relayData = [];

                // Process each relay's data, maintaining continuity
                relayDataMap[relay]?.forEach((point, index) => {
                    if (lastRelay !== relay && lastValue !== null) {
                        // Inject a connection point if transitioning from a different relay
                        relayData.push({
                            value: lastValue,
                            name: point.time,
                            relay,
                        });
                    }
                    // Add the current data point
                    relayData.push({
                        value: point.value,
                        name: point.time,
                        relay: point.relay,
                    });

                    lastRelay = relay;
                    lastValue = point.value;
                });

                return {
                    name: `Relay ${relay}`,
                    type: "line",
                    data: relayData,
                    color: relayColors[relay],
                    smooth: true,
                    showSymbol: false,
                    lineStyle: {
                        width: 4, // Adjust this value for the desired line width
                    },
                };
            });
        })(),
    };


    return (
        <div className="p-8 font-sans bg-white min-h-screen relative">

            {/* Real-time bar for instant flow */}
            <div className="absolute top-8 right-8 bg-white p-8 rounded shadow border w-64 z-10 border-gray-600">
                <h2 className="text-xl font-bold text-gray-700 mb-4 text-blue-900">即時氣量</h2>
                <div className="relative h-8 w-full bg-gray-200 rounded">
                    <div
                        className="absolute h-full bg-purple-500 rounded"
                        style={{ width: `${Math.min((instantFlow / 16) * 100, 100)}%` }}
                    ></div>
                </div>
                <p className="text-center mt-4 text-lg font-semibold text-gray-700">
                    {instantFlow.toFixed(2)} L/s ({Math.min((instantFlow / 16) * 100, 100).toFixed(1)}%)
                </p>
            </div>



            {/* Relay Control Section */}
            <div className="w-2/5 bg-gray-200 mx-auto p-6 rounded shadow-md border border-gray-400">
                <h2 className="text-xl font-semibold mb-4 text-center text-blue-900">繼電器控制</h2>
                <div className="flex justify-between items-center gap-4">
                    {[3, 2, 1].map((relay) => (
                        <button
                            key={relay}
                            className={`flex-1 px-6 py-3 rounded text-white text-lg font-medium shadow-md transition ${relayStatus[relay] === "ON"
                                ? "bg-green-600 hover:bg-green-700"
                                : "bg-gray-600 hover:bg-gray-500"
                                }`}
                            onClick={() => handleRelayToggle(relay)}
                        >
                            {relay === 2 ? "全開(2)" : relay === 3 ? "左側(3)" : "右側(1)"}：
                            {relayStatus[relay] === "ON" ? "開啟" : "關閉"}
                        </button>
                    ))}
                </div>

                {/* <button
                    className={`flex-1 px-6 py-3 rounded text-white text-lg font-medium shadow-md transition ${autoTestInterval ? "bg-red-600 hover:bg-red-700" : "bg-blue-600 hover:bg-blue-700"}`}
                    onClick={handleAutoTest}
                >
                    {autoTestInterval ? "停止測試" : "自動測試"}
                </button> */}
            </div>

            {/* Chart Section */}
            <ReactECharts option={chartOptions} style={{ height: "400px", width: "100%" }} />

            <div className="p-8 font-sans bg-gray-200 min-h-screen relative">
                <h2 className="text-2xl font-semibold text-gray-700">儲存的專案</h2>
                <ul className="list-disc ml-6 relative">
                    {savedProjects.map((project, index) => {
                        const relayOrder = ["3", "2", "1"];

                        const meanString = project.mean
                            ? Object.entries(project.mean)
                                .filter(([relay]) => relayOrder.includes(relay))
                                .sort(([relayA], [relayB]) => relayOrder.indexOf(relayA) - relayOrder.indexOf(relayB))
                                .map(([relay, { name, value }]) => {
                                    const percentage = project.percentages[relay];
                                    return `<span>${name}:</span> <span class="text-orange-800 font-bold text-2xl">${value}</span><span class="text-gray-600 text-sm"> (${percentage}%)</span>`;
                                })
                                .join(
                                    `<span style="display: inline-block; margin: 0 20px; font-size: 1.5em;">/</span>`
                                )
                            : "No data";

                        const warningMessage = project.hasLowPerformance
                            ? `<span class="text-blue-600 text-2xl ml-4">有一孔阻塞超過50%, 建議更換</span>`
                            : '';

                        return (
                            <li
                                key={index}
                                onMouseEnter={(event) => handleMouseEnter(event, project)}
                                onMouseLeave={handleMouseLeave}
                                className="relative cursor-pointer"
                                dangerouslySetInnerHTML={{
                                    __html: `${project.name}（數據量: ${project.數據量}） <span class="ml-2 text-gray-500">${meanString}</span>${warningMessage}`,
                                }}
                            ></li>
                        );
                    })}
                </ul>




                {/* Tooltip for JSON data */}
                {hoveredProject && (
                    <div
                        className="absolute bg-white p-4 shadow-lg border rounded w-64 z-10"
                        style={{
                            ...tooltipStyle,
                            position: "fixed",
                        }}
                    >
                        <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                            {JSON.stringify(hoveredProject, null, 2)}
                        </pre>
                    </div>
                )}
            </div>
        </div>
    );
};

export default MqttPage;
