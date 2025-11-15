// Glow Effect Fragment Shader
precision mediump float;
uniform vec4 u_color;
uniform float u_intensity;
varying vec2 v_texCoord;

void main() {
    float glow = u_intensity * (1.0 - length(v_texCoord - vec2(0.5)));
    gl_FragColor = vec4(u_color.rgb * glow, u_color.a * glow);
}
