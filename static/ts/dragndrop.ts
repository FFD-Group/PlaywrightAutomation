
import Alpine from 'alpinejs'

window.Alpine = Alpine

class FormElement {
    required: Boolean;
    type: String;
    value: String;
    validation?: String;

    constructor(r: Boolean, t: String, v: String, validation?: String) {
        this.required = r;
        this.type = t;
        this.value = v;
        this.validation = validation;
    }
}

class ValidationResult {
    passed: Boolean;
    form_els: Array<FormElement> = [];

    constructor(p: Boolean, els?: Array<FormElement>|FormElement) {
        this.passed = p;
        if (els !== undefined && Array.isArray(els)) {
            this.form_els = els;
        } else if (els !== undefined) {
            this.form_els.push(els);
        }
    }
}

class Action {
    id: number = 0;
    form_els: Array<FormElement> = [];

    public validate(): ValidationResult  {
        let result = new ValidationResult(true);

        return result;
    }
}

class ActionList {
    actions: Array<Action> = [];

    addAction(action: Action): undefined {
        this.actions.push(action);
    }

    removeAction(action: Action): undefined {
        let index = this.actions.indexOf(action);
        if (index > -1) this.actions.splice(index, 1);
    }

    clearActions(): undefined {
        this.actions = [];
    }
}

class Automation {

    constructor() {
        console.log("Automation created!");
    }
    
    dragOverHandler(ev: DragEvent) {
        ev.preventDefault();
        if (ev.dataTransfer) {
            ev.dataTransfer.dropEffect = "copy";
        }
    }
    
    dropHandler(ev: DragEvent) {
        ev.preventDefault();
        if (ev.dataTransfer && ev.target) {
            const data = ev.dataTransfer.getData("text/html");
            (ev.target as HTMLElement).appendChild(document.getElementById(data)!);
        }
    }
}

document.addEventListener('alpine:init', () => {
    Alpine.data('actionlist', () => (
        new ActionList()
    ));
    Alpine.data('automation', () => (
        new Automation()
    ))
});

Alpine.start()