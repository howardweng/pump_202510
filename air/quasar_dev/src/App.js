import { useEffect } from "react";
import { Routes, Route, useNavigationType, useLocation, Link } from "react-router-dom";
import Flow from "./pages/Flow";     // Import the Flow page (renamed from Home.js)
import Control from "./pages/Control"; // Import the Temperature Control (Control) page
import { FiRefreshCw } from "react-icons/fi";


function App() {
  const action = useNavigationType();
  const location = useLocation();

  useEffect(() => {
    // Scroll to the top on navigation (except for browser back/forward)
    if (action !== "POP") {
      window.scrollTo(0, 0);
    }
  }, [action]);

  useEffect(() => {
    // Set dynamic page title and meta description based on the route
    const pageDetails = {
      "/flow": {
        title: "流量控制",
        description: "管理流量數據與相關設定。",
      },
      "/": {
        title: "溫度控制",
        description: "管理溫度數據與相關設定。",
      },
    };

    const { title, description } = pageDetails[location.pathname] || {
      title: "控制系統",
      description: "監控並管理設備數據。",
    };

    document.title = title;
    const metaDescriptionTag = document.querySelector('head > meta[name="description"]');
    if (metaDescriptionTag) {
      metaDescriptionTag.content = description;
    } else {
      const newMetaTag = document.createElement("meta");
      newMetaTag.name = "description";
      newMetaTag.content = description;
      document.head.appendChild(newMetaTag);
    }
  }, [location.pathname]);

  const currentPath = location.pathname;

  return (
    <>
      {/* Header with Navigation Buttons */}
      <header className="bg-gray-100 text-gray-800 py-2 shadow-sm relative">
        <nav className="container mx-auto flex justify-center gap-4">
          <button
            onClick={() => {
              console.log("🔄 Page reload triggered! Current path:", window.location.pathname);
              window.location.href = "/"; // Forces a full reload
            }}
            className={`px-6 py-2 rounded bg-blue-600 text-white text-lg font-medium shadow-md transition ${currentPath === "/" ? "opacity-50 pointer-events-none" : "hover:bg-blue-500"
              }`}
          >
            加熱器溫度控制
          </button>

          <button
            onClick={() => {
              console.log("🔄 Page reload triggered! Current path:", window.location.pathname);
              window.location.href = "/flow"; // Forces a full reload
            }}
            className={`px-6 py-2 rounded bg-blue-600 text-white text-lg font-medium shadow-md transition ${currentPath === "/flow" ? "opacity-50 pointer-events-none" : "hover:bg-blue-500"
              }`}
          >
            氣體流量
          </button>

        </nav>


        {/* Refresh Button at the Very Right */}
        <button
          onClick={() => window.location.reload()}
          className="absolute top-1/2 right-4 transform -translate-y-1/2 px-6 py-2 flex items-center gap-2 rounded bg-green-800 text-white text-lg font-medium shadow-md transition hover:bg-green-600"
        >
          <FiRefreshCw className="w-6 h-6" /> {/* ✅ Refresh icon */}
          <span>重新整理頁面</span>
        </button>
      </header>


      <Routes>
        {/* Root route now shows Control page */}
        <Route path="/" element={<Control />} />
        {/* Flow page route */}
        <Route path="/flow" element={<Flow />} />
      </Routes>
    </>
  );
}

export default App;
