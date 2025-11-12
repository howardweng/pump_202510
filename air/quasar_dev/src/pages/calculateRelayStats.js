export function calculateRelayStats(data = [], baseMean = 15, threshold = 50, z_threshold = 2) {
    // Group data by relay, ignoring points where time < 1 second.
    const relayGroups = data.reduce((acc, { relay, value, time }) => {
        // Convert time to a number if it's a string.
        const t = typeof time === "string" ? parseFloat(time) : time;
        if (t >= 1) { // Ignore data before 1 second.
            if (!acc[relay]) acc[relay] = [];
            acc[relay].push(value);
        }
        return acc;
    }, {});

    // Calculate stats for each relay
    const relayStats = Object.fromEntries(
        Object.entries(relayGroups).map(([relay, values]) => {
            if (values.length === 0) {
                console.warn(`Relay ${relay}: No data available after 1 second.`);
                return [relay, { mean: 0, stdDev: 0 }];
            }

            // Sort values for consistency
            const useValues = [...values].sort((a, b) => a - b);

            // Calculate raw mean and standard deviation
            const rawMean = useValues.reduce((sum, v) => sum + v, 0) / useValues.length;
            const variance = useValues.reduce((sum, v) => sum + Math.pow(v - rawMean, 2), 0) / useValues.length;
            const stdDev = Math.sqrt(variance);

            // Filter out outliers using Z-score threshold
            const zFilteredValues = stdDev === 0
                ? useValues
                : useValues.filter(v => {
                    const zScore = Math.abs(v - rawMean) / stdDev;
                    return zScore <= z_threshold;
                });

            // Calculate mean based on filtered values (if available)
            const mean = zFilteredValues.length > 0
                ? zFilteredValues.reduce((sum, v) => sum + v, 0) / zFilteredValues.length
                : rawMean;

            return [relay, { mean: parseFloat(mean.toFixed(2)), stdDev: parseFloat(stdDev.toFixed(2)) }];
        })
    );

    // Map relay to its computed mean
    const meanValues = Object.fromEntries(
        Object.entries(relayStats).map(([relay, stats]) => [relay, stats.mean])
    );

    // Calculate relay percentages based on baseMean
    const relayPercentages = Object.fromEntries(
        Object.entries(meanValues).map(([relay, mean]) => {
            const percentage = ((mean / baseMean) * 100).toFixed(1) + "%";
            return [relay, percentage];
        })
    );

    // Check only relay 1 and relay 3:
    // If either relay 1 or relay 3 has a percentage less than the threshold, needChange will be true.
    const needChange = ["1", "3"].some((relay) => {
        const mean = meanValues[relay] || 0;
        const percentString = relayPercentages[relay] || "0%";
        const percentValue = parseFloat(percentString.replace("%", ""));
        // Trigger needChange if percentage is below threshold OR the mean is 0.
        return percentValue < threshold || mean === 0;
    });


    return {
        baseMean: baseMean.toFixed(2),
        meanValues,
        relayPercentages,
        needChange
    };
}
