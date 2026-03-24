import { app } from "../../../scripts/app.js";

// Character Selector JS to handle character previews
app.registerExtension({
    name: "CharacterSelector.Preview",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "CharacterSelector") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

                // Create a generic placeholder for the image
                const imgWidget = {
                    type: "HTML",
                    name: "preview",
                    draw(ctx, node, widget_width, y, widget_height) {
                        if (!this.img || !this.img.complete || this.img.naturalWidth === 0) return;
                        
                        const margin = 10;
                        const width = widget_width - margin * 2;
                        const aspectRatio = this.img.naturalHeight / this.img.naturalWidth;
                        const height = width * aspectRatio;
                        
                        ctx.drawImage(this.img, margin, y, width, height);
                        this.computedHeight = height + 10;
                    },
                    computeSize() {
                        return [200, this.computedHeight || 0];
                    },
                    computedHeight: 0,
                    img: new Image()
                };
                
                this.addCustomWidget(imgWidget);

                const characterWidget = this.widgets.find(w => w.name === "character_name");
                
                const updateImage = async () => {
                    const name = characterWidget.value;
                    if (!name || name === "None") {
                        imgWidget.img.src = "";
                        imgWidget.computedHeight = 0;
                        return;
                    }
                    
                    try {
                        const response = await fetch(`/character_selector/get_characters`);
                        const data = await response.json();
                        const character = data.find(c => c.name === name);
                        
                        if (character && character.cover) {
                            // Point to the custom route that serves the image
                            imgWidget.img.src = `/character_selector/view_cover?filename=${encodeURIComponent(character.cover)}`;
                            imgWidget.img.onload = () => {
                                this.setDirtyCanvas(true, true);
                            };
                        } else {
                            imgWidget.img.src = "";
                            imgWidget.computedHeight = 0;
                        }
                    } catch (e) {
                        console.error("Failed to load character preview", e);
                        imgWidget.img.src = "";
                        imgWidget.computedHeight = 0;
                    }
                    this.setDirtyCanvas(true, true);
                };

                // Update when widget value changes
                const callback = characterWidget.callback;
                characterWidget.callback = function () {
                    if (callback) callback.apply(this, arguments);
                    updateImage();
                };

                // Initial load
                setTimeout(updateImage, 100);

                return r;
            };
        }
    }
});
