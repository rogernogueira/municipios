window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, context) {
            const {
                classes,
                colorscale,
                style,
                colorProp
            } = context.props.hideout; // get props from hideout
            const value = feature.properties[colorProp]; // get value the determines the color
            console.log('valor', value);
            if (value > 0) {
                style.fillColor = colorscale[1]; // set the fill color according to the class
            } else {
                style.fillColor = colorscale[0];
            };
            return style;
        }
    }
});