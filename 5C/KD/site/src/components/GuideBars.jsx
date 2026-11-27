import './GuideBars.css';

export default function GuideBars({ variant }) {
  if (variant !== 'wireframe') {
    return null;
  }
  return (
    <>
      <div className="guides guides-desktop" aria-hidden="true">
        {Array.from({ length: 12 }, (_, i) => (
          <div key={i} />
        ))}
      </div>
      <div className="guides guides-mobile" aria-hidden="true">
        {Array.from({ length: 8 }, (_, i) => (
          <div key={i} />
        ))}
      </div>
    </>
  );
}
