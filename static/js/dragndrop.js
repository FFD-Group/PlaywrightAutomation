document.addEventListener('alpine:init', () => {

    Alpine.data('action', () => ({
        form_els: [],
        pw_method: '',
        pw_method_arg: '',

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

        validate()  {
            let result = new ValidationResult(true);

            return result;
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


    Alpine.data('actionlist', () => ({
        actions,

        addAction(action) {
            this.actions.push(action);
        },

        removeAction(action) {
            let index = this.actions.indexOf(action);
            if (index > -1) this.actions.splice(index, 1);
        }
    }));

    Alpine.data('automation', () => ({
        action_list: [],
        
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
            newAction.removeChild(grabhandle);
            newAction.removeAttribute("draggable");
        },

        clearList() {
            this.action_list = [];
            let targetHtml = document.getElementById("target");
            targetHtml.querySelectorAll("div.action").forEach((div) => {
                targetHtml.removeChild(div);
            });
        }
    }));
});