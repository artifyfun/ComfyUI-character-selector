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
                    type: "CHARACTER_PREVIEW",
                    name: "preview",
                    draw(ctx, node, widget_width, y, widget_height) {
                        if (!this.img || !this.img.complete || this.img.naturalWidth === 0) return;
                        
                        const margin = 10;
                        const width = widget_width - margin * 2;
                        const aspectRatio = this.img.naturalHeight / this.img.naturalWidth;
                        const height = width * aspectRatio;
                        
                        ctx.drawImage(this.img, margin, y, width, height);
                    },
                    computeSize() {
                        const width = this.node ? this.node.size[0] : 200;
                        if (this.img && this.img.complete && this.img.naturalWidth > 0) {
                            const aspectRatio = this.img.naturalHeight / this.img.naturalWidth;
                            return [width, (width - 20) * aspectRatio + 10];
                        }
                        return [width, this.img && this.img.src ? 100 : 0];
                    },
                    node: this,
                    img: new Image()
                };
                
                this.addCustomWidget(imgWidget);

                const characterWidget = this.widgets.find(w => w.name === "character_name");
                
                const updateImage = async () => {
                    const name = characterWidget.value;
                    if (!name || name === "None") {
                        imgWidget.img.src = "";
                        this.setSize(this.computeSize());
                        return;
                    }
                    
                    try {
                        const response = await fetch(`/character_selector/get_characters`);
                        const data = await response.json();
                        const character = data.find(c => c.name === name);
                        
                        if (character && character.cover) {
                            const newSrc = `/character_selector/view_cover?filename=${encodeURIComponent(character.cover)}`;
                            if (imgWidget.img.src !== newSrc) {
                                imgWidget.img.src = newSrc;
                                imgWidget.img.onload = () => {
                                    this.setSize(this.computeSize());
                                    this.setDirtyCanvas(true, true);
                                };
                            }
                        } else {
                            imgWidget.img.src = "";
                            this.setSize(this.computeSize());
                        }
                    } catch (e) {
                        console.error("Failed to load character preview", e);
                        imgWidget.img.src = "";
                        this.setSize(this.computeSize());
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
