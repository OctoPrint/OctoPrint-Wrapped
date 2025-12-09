ko.bindingHandlers["src.svgtopng"] = {
    init: (element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) => {
        const value = valueAccessor();
        const valueUnwrapped = ko.unwrap(value);
        if (!valueUnwrapped) return;

        const $element = $(element);

        $.get(valueUnwrapped).done((data, textStatus, xhr) => {
            const svgString = xhr.responseText;

            const svg = new Blob([svgString], {
                type: "image/svg+xml;charset=utf-8"
            });

            const url = URL.createObjectURL(svg);

            const img = new Image();
            img.onload = () => {
                URL.revokeObjectURL(url);

                const canvas = document.createElement("canvas");
                canvas.width = img.width;
                canvas.height = img.height;

                const ctx = canvas.getContext("2d");
                ctx.drawImage(img, 0, 0);

                const png = canvas.toDataURL("image/png");
                $element.attr("src", png);
            };
            img.src = url;
        });
    }
};
ko.bindingHandlers["src.svgtopng"].update = ko.bindingHandlers["src.svgtopng"].init;
