import { ComponentProps } from "solid-js"

export const Mark = (props: { class?: string }) => {
  return (
    <span
      data-component="logo-mark"
      classList={{ [props.class ?? ""]: !!props.class }}
      style={{ "font-size": "1.25rem", "line-height": "1" }}
    >
      🌯
    </span>
  )
}

export const Splash = (props: Pick<ComponentProps<"svg">, "ref" | "class">) => {
  return (
    <div
      ref={props.ref as any}
      data-component="logo-splash"
      classList={{ [props.class ?? ""]: !!props.class }}
      style={{
        display: "flex",
        "align-items": "center",
        "justify-content": "center",
        "font-size": "4rem",
      }}
    >
      🌯
    </div>
  )
}

export const Logo = (props: { class?: string }) => {
  return (
    <div
      classList={{ [props.class ?? ""]: !!props.class }}
      style={{
        display: "flex",
        "align-items": "center",
        gap: "0.5rem",
        "font-weight": "700",
        "font-size": "1.25rem",
        color: "var(--text-strong)",
      }}
    >
      <span style={{ "font-size": "1.5rem" }}>🌯</span>
      chipotlai max
    </div>
  )
}
