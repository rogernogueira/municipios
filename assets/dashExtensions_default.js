window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, context) {
            const {
                classes,
                colorscale,
                style,
                colorProp
            } = context.props.hideout; // get props from 
            const value = feature.properties[colorProp]; // get value the determines the color
            if (value > 0) {
                style.fillColor = colorscale[1]; // set the fill color according to the class
            } else {
                style.fillColor = colorscale[0];
            };
            return style;
        },
        function1: function(feature, context) {
            const {
                classes,
                colorscale,
                style,
                colorProp
            } = context.props.hideout; // get props from hideout
            const value = feature.properties[colorProp]; // get value the determines the color
            const quad = feature.properties['quadrantes']; // get value the determines the color


            if (value > 0) {
                if (quad == 1) {
                    style.fillColor = colorscale[1];
                } else if (quad == 2) {
                    style.fillColor = colorscale[2];
                } else if (quad == 3) {
                    style.fillColor = colorscale[3];
                } else if (quad == 4) {
                    style.fillColor = colorscale[4];
                }

            } else {
                style.fillColor = colorscale[0];
            };
            return style;
        },
        function2: function(feature, context) {
            const {
                classes,
                colorscale,
                style,
                colorProp
            } = context.props.hideout; // get props from hideout
            const value = feature.properties[colorProp]; // get value the determines the color
            for (let i = 0; i < classes.length; ++i) {
                if (value > classes[i]) {
                    style.fillColor = colorscale[i]; // set the fill color according to the class
                }
            }

            return style;
        },
        function3: function(feature, context) {
            const {
                classes,
                colorscale,
                style,
                colorProp
            } = context.props.hideout; // get props from hideout
            const value = feature['properties']['População']; // get value the determines the color

            for (let i = 0; i < classes.length; ++i) {
                if (value > classes[i]) {
                    style.fillColor = colorscale[i]; // set the fill color according to the class
                }
            }

            return style;
        }
    }
});