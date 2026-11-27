import './Placeholder.css';

/**
 * Single media component used everywhere.
 * - wireframe: gray placeholder box (never an <img>)
 * - full: real photo when `src` is provided
 */
export default function Placeholder({ src, alt = '', className = '' }) {
  if (src) {
    return <img className={`ph ${className}`} src={src} alt={alt} loading="lazy" />;
  }
  return <div className={`ph ${className}`} />;
}
