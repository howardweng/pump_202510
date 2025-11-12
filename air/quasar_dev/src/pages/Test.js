import React, { useState, useEffect, useRef } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import html2canvas from "html2canvas";

const SimpleChartPage = () => {
    const [data, setData] = useState([]);
    const [time, setTime] = useState(0);
    const [filenameSuffix, setFilenameSuffix] = useState("");
    const chartRef = useRef(null);

    useEffect(() => {
        let interval;
        if (time < 10) {
            interval = setInterval(() => {
                setData((prevData) => [
                    ...prevData,
                    {
                        time: time,
                        value: Math.random() * 100, // Generate random value
                    },
                ]);
                setTime((prevTime) => prevTime + 1);
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [time]);

    const getTimestamp = () => {
        const now = new Date();
        return `${now.getFullYear()}-${(now.getMonth() + 1).toString().padStart(2, '0')}-${now.getDate().toString().padStart(2, '0')}_` +
            `${now.getHours().toString().padStart(2, '0')}-${now.getMinutes().toString().padStart(2, '0')}-${now.getSeconds().toString().padStart(2, '0')}`;
    };

    const downloadChart = () => {
        if (chartRef.current) {
            html2canvas(chartRef.current).then((canvas) => {
                const link = document.createElement("a");
                link.href = canvas.toDataURL("image/png");
                const suffix = filenameSuffix.trim() ? `_${filenameSuffix}` : "";
                link.download = `chart_${getTimestamp()}${suffix}.png`;
                link.click();
            });
        }
    };

    return (
        <div className="p-8 bg-white min-h-screen flex flex-col items-center">
            <h2 className="text-xl font-bold mb-4">簡單數據圖表</h2>

            <div ref={chartRef} className="w-full flex justify-center">
                <ResponsiveContainer width="80%" height={300}>
                    <LineChart data={data}>
                        <CartesianGrid stroke="#ccc" />
                        <XAxis dataKey="time" tickFormatter={(tick) => `${tick}s`} />
                        <YAxis domain={[0, 100]} />
                        <Tooltip />
                        <Line type="monotone" dataKey="value" stroke="blue" strokeWidth={2} dot={false} name="隨機數值" />
                    </LineChart>
                </ResponsiveContainer>
            </div>
            <input
                type="text"
                placeholder="輸入文件名稱後綴..."
                value={filenameSuffix}
                onChange={(e) => setFilenameSuffix(e.target.value)}
                className="mb-4 px-4 py-2 border border-gray-300 rounded-lg w-1/3 max-w-xs focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm transition duration-200"
            />


            <button onClick={downloadChart} className="mt-4 px-4 py-2 bg-blue-500 text-white rounded">下載圖表</button>
        </div>
    );
};

export default SimpleChartPage;
