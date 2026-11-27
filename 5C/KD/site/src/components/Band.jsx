import GuideBars from './GuideBars.jsx';
import './Band.css';

/**
 * The ONE content container of the site.
 *
 * Owns the horizontal insets (150px desktop / 16px mobile), hosts the
 * wireframe guide bars as an internal overlay, and clips its subtree:
 * children may only shrink, never paint or lay out outside the band.
 */
export default function Band({ variant, children }) {
  return (
    <div className="band">
      <GuideBars variant={variant} />
      {children}
    </div>
  );
}
