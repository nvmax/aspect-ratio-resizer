import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "aspectratioresizer.extension",
    
    async setup() {
        // Add event listener for resize information messages
        function resizeInfoHandler(event) {
            const data = event.detail;

            // Create a formatted message showing resize information
            let message = `Aspect Ratio Resizer Results:\n`;
            message += `Constraints: ${data.constraints}\n`;
            message += `Resize Mode: ${data.resize_mode}\n`;
            message += `Width Enabled: ${data.enable_width}\n`;
            message += `Height Enabled: ${data.enable_height}\n`;
            message += `Batch Size: ${data.batch_size}\n\n`;

            data.resize_info.forEach((info, index) => {
                let line = `Image ${index + 1}: ${info.original} → ${info.new} (scale: ${info.scale})`;
                if (info.constraint) {
                    line += ` [${info.constraint}]`;
                }
                message += line + '\n';
            });

            // Log to console for debugging
            console.log("Aspect Ratio Resizer:", data);

            // Show a brief notification (you can customize this)
            if (data.resize_info.some(info => info.new !== "unchanged" && !info.new.includes("unchanged"))) {
                console.log(message);
                // Optionally show a toast notification or update UI
                // You can uncomment the line below if you want a popup alert
                // alert(message);
            }
        }
        
        // Add event listener for auto megapixel reducer messages
        function megapixelReducerHandler(event) {
            const data = event.detail;

            // Create a formatted message showing resize information
            let message = `Auto Megapixel Reducer Results:\n`;
            message += `Target: ${data.max_megapixels}MP\n`;
            message += `Original: ${data.original_megapixels.toFixed(2)}MP\n`;
            message += `Only Reduce Mode: ${data.only_reduce}\n`;
            message += `Batch Size: ${data.batch_size}\n\n`;

            data.resize_info.forEach((info, index) => {
                let line = `Image ${index + 1}: ${info.original} → ${info.new}`;
                line += ` (${info.megapixels}) [scale: ${info.scale}]`;
                message += line + '\n';
            });

            // Log to console for debugging
            console.log("Auto Megapixel Reducer:", data);

            // Show a brief notification if any images were resized
            if (data.resize_info.some(info => info.new !== "unchanged" && !info.new.includes("unchanged"))) {
                console.log(message);
                // Optionally show a toast notification or update UI
                // You can uncomment the line below if you want a popup alert
                // alert(message);
            }
        }

        // Register the event listeners
        app.api.addEventListener("aspectratioresizer.resize_info", resizeInfoHandler);
        app.api.addEventListener("automegapixelreducer.resize_info", megapixelReducerHandler);
    },
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // Add custom styling or behavior to the AspectRatioResizer node
        if (nodeData.name === "AspectRatioResizer") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;

            nodeType.prototype.onNodeCreated = function () {
                const result = onNodeCreated?.apply(this, arguments);

                // Add a title to make the node more identifiable
                this.title = "Aspect Ratio Resizer";

                // Set a custom color for the node (optional)
                this.color = "#2a4d3a";
                this.bgcolor = "#335544";

                return result;
            };
        }

        // Add custom styling for the AutoMegapixelReducer node
        if (nodeData.name === "AutoMegapixelReducer") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;

            nodeType.prototype.onNodeCreated = function () {
                const result = onNodeCreated?.apply(this, arguments);

                // Add a title to make the node more identifiable
                this.title = "Auto Megapixel Reducer";

                // Set a custom color for the node (optional) - different from the first node
                this.color = "#4d2a3a";
                this.bgcolor = "#553344";

                return result;
            };
        }
    }
});
