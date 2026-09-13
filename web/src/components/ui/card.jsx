export function Card({ children, className = '', ...props }) { return <section className={`card ${className}`} {...props}>{children}</section>; }
export function CardHeader({ children, ...props }) { return <header {...props}>{children}</header>; }
export function CardTitle({ children, ...props }) { return <h2 {...props}>{children}</h2>; }
export function CardContent({ children, ...props }) { return <div {...props}>{children}</div>; }
