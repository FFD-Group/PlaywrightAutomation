document.addEventListener('alpine:init', () => {

    Alpine.data('action', () => ({
        form_els: [],
        pw_method: 'text',
        pw_method_arg: '',
        pw_method_arg_2: '',

        constructor(htmlAction) {
            if (htmlAction) {
                this.populateFormElements(htmlAction);
                htmlAction.removeAttribute("draggable");
            }
        },

        populateFormElements(el) {
            el.querySelectorAll("select,input").forEach((htmlFormEl) => {
                let required = htmlFormEl.hasAttribute("required");
                let type = htmlFormEl.tagName;
                let value = (htmlFormEl).value;
                let validation = htmlFormEl.getAttribute("pattern") || undefined;
                let fe = new FormElement(required, type, value, validation);
                this.form_els.push(fe);
            });
        },

        dragStartHandler(ev) {
            if (ev.target instanceof Element && ev.target.classList.contains("action")) {
                ev.target.classList.add("dragging");
                Alpine.store("dragged", ev.target);
            }
        },

        dragEndHandler(ev) {
            if (ev.target instanceof Element && ev.target.classList.contains("action")) {
                ev.target.classList.remove("dragging");
                Alpine.store("dragged", undefined);
            }
        }
    }));

    Alpine.data('automation', () => ({
        action_list: [],
        start_url: "",
        
        dragOverHandler(ev) {
            ev.preventDefault();
            if (ev.dataTransfer) {
                ev.dataTransfer.dropEffect = "copy";
            }
        },
        
        dropHandler(ev) {
            ev.preventDefault();
            let dropTarget = document.getElementById("target");
            let newAction = Alpine.store("dragged").cloneNode(true);
            newAction.classList.remove("dragging");
            dropTarget.appendChild(newAction);
            this.action_list.push(newAction);
            let grabhandle = newAction.querySelector(".grabhandle");
            let title = grabhandle.querySelector("h3.title");
            newAction.insertBefore(title, grabhandle);
            newAction.removeChild(grabhandle);
            newAction.removeAttribute("draggable");
        },

        clearList() {
            this.action_list = [];
            let targetHtml = document.getElementById("target");
            targetHtml.querySelectorAll("div.action:not(.gotopage-action)").forEach((div) => {
                targetHtml.removeChild(div);
            });
        },

        _checkUrlValid(input) {
            let url;
            try {
                url = new URL(input);
            } catch (_) {
                return false;
            }
            return true;
        },

        _markActionInvalid(htmlAction) {
            i
        },

        _clearValidation() {
            startAction = document.querySelector("#starting-action input");
            startAction.classList.remove("invalid-input");
            startAction.classList.remove("animate-pulse");
            this.action_list.forEach((htmlAction) => {
                htmlAction.querySelectorAll("input").forEach((input) => {
                    input.classList.remove("invalid-input");
                    input.classList.remove("animate-pulse");
                })
            });
        },

        validate() {
            this._clearValidation();
            let valid = true;
            // check start URL is valid
            if (!this._checkUrlValid(this.start_url)) {
                startAction = document.querySelector("#starting-action input");
                startAction.classList.add("invalid-input");
                startAction.classList.add("animate-pulse");
                valid = false;
            }
            // check there is at least 1 action
            if (this.action_list.length <= 0) {
                valid = false;
            }
            // check each action is valid
            this.action_list.forEach((htmlAction) => {
                htmlAction.querySelectorAll("input").forEach((input) => {
                    if (input.value.trim() === "") {
                        valid = false;
                        input.classList.add("invalid-input");
                        input.classList.add("animate-pulse");
                    }
                })
            });
            console.log("Validate returning: ", valid);
            return valid;
        }
    }));
});