document.addEventListener('alpine:init', () => {

    Alpine.data('flash', () => ({
        message: '',

        loadMessage() {
            const queryString = window.location.search;
            const urlParams = new URLSearchParams(queryString);
            if (urlParams.has("automation_id") && urlParams.has("supplier_name")) {
                automation_id=urlParams.get("automation_id");
                supplier_name=urlParams.get("supplier_name");
                this.message = `Automation ID: ${automation_id} saved for ${supplier_name}.`;
                setTimeout(() => {
                    this.message = '';
                }, 5000);
            }
        }
    }));
});