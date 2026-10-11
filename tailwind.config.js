
module.exports = {
  content: ["./templates/**/*.html"],
  darkMode: "class",
  theme: {
    extend: {
      colors: { "on-tertiary": "#ffffff", "on-primary-container": "#d3ffd5", "on-background": "#131b2e", "primary-container": "#15803d", "surface-container-high": "#e2e7ff", "on-error-container": "#93000a", "secondary-fixed": "#ffddb0", "tertiary-fixed-dim": "#4ae176", "surface-tint": "#006d30", "tertiary-container": "#008138", "error-container": "#ffdad6", "secondary": "#805600", "on-primary-fixed": "#00210a", "on-error": "#ffffff", "surface-container-lowest": "#ffffff", "secondary-container": "#feb63c", "primary-fixed": "#95f8a7", "on-surface": "#131b2e", "surface-dim": "#d2d9f4", "tertiary-fixed": "#6bff8f", "outline-variant": "becabc", "primary-fixed-dim": "#79db8d", "on-secondary-container": "#6e4900", "on-tertiary-fixed": "#002109", "surface-variant": "#dae2fd", "on-secondary-fixed": "#281800", "inverse-surface": "#283044", "primary": "#00652c", "tertiary": "#00652b", "surface-container": "#eaedff", "outline": "#6f7a6e", "surface-container-low": "#f2f3ff", "surface-bright": "#faf8ff", "on-tertiary-container": "#d5ffd5", "inverse-on-surface": "#eef0ff", "on-primary-fixed-variant": "#005323", "error": "#ba1a1a", "on-secondary-fixed-variant": "#614000", "secondary-fixed-dim": "#ffba46", "on-primary": "#ffffff", "surface-container-highest": "#dae2fd", "on-surface-variant": "#3f493f", "on-tertiary-fixed-variant": "#005321", "surface": "#faf8ff", "on-secondary": "#ffffff", "background": "#faf8ff", "inverse-primary": "#79db8d" },
      borderRadius: { "DEFAULT": "0.25rem", "lg": "0.5rem", "xl": "0.75rem", "full": "9999px" },
      spacing: { "space-lg": "2rem", "space-md": "1.25rem", "space-xl": "3rem", "margin-desktop": "3rem", "space-xs": "0.375rem", "gutter-tablet": "1.5rem", "margin": "1rem", "gutter-desktop": "2rem", "margin-tablet": "2rem", "space-sm": "0.75rem", "gutter": "1rem" },
      fontFamily: {
        "body-md": ["system-ui", "sans-serif"],
        "label-sm": ["system-ui", "sans-serif"],
        "label-lg": ["system-ui", "sans-serif"],
        "headline-sm": ["system-ui", "sans-serif"],
        "headline-md": ["system-ui", "sans-serif"],
        "headline-lg-mobile": ["system-ui", "sans-serif"],
        "body-lg": ["system-ui", "sans-serif"],
        "headline-xl-mobile": ["system-ui", "sans-serif"],
        "label-md": ["system-ui", "sans-serif"],
        "body-sm": ["system-ui", "sans-serif"],
        "headline-xl": ["system-ui", "sans-serif"],
        "headline-lg": ["system-ui", "sans-serif"]
      },
      fontSize: {
        "body-md": ["16px", { "lineHeight": "24px", "fontWeight": "500" }],
        "label-sm": ["12px", { "lineHeight": "16px", "letterSpacing": "0.06em", "fontWeight": "800" }],
        "label-lg": ["16px", { "lineHeight": "20px", "letterSpacing": "0.02em", "fontWeight": "800" }],
        "headline-sm": ["18px", { "lineHeight": "24px", "fontWeight": "700" }],
        "headline-md": ["22px", { "lineHeight": "28px", "fontWeight": "700" }],
        "headline-lg-mobile": ["26px", { "lineHeight": "32px", "letterSpacing": "-0.01em", "fontWeight": "800" }],
        "body-lg": ["18px", { "lineHeight": "26px", "fontWeight": "600" }],
        "headline-xl-mobile": ["32px", { "lineHeight": "38px", "letterSpacing": "-0.02em", "fontWeight": "800" }],
        "label-md": ["14px", { "lineHeight": "18px", "letterSpacing": "0.04em", "fontWeight": "800" }],
        "body-sm": ["14px", { "lineHeight": "20px", "fontWeight": "600" }],
        "headline-xl": ["40px", { "lineHeight": "48px", "letterSpacing": "-0.02em", "fontWeight": "800" }],
        "headline-lg": ["30px", { "lineHeight": "36px", "letterSpacing": "-0.01em", "fontWeight": "800" }]
      }
    }
  }
};

