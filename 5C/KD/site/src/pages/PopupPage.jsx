import { Link, useParams } from 'react-router-dom';
import Band from '../components/Band.jsx';
import { POPUPS, POPUP_IDS } from '../content/popups.js';
import './PopupPage.css';

function MenuPopup({ popup }) {
  return (
    <div className="modal">
      <div className="menu-header">
        <div className="logo">Матпрофи</div>
        <div className="close">✕</div>
      </div>
      <nav className="menu-nav">
        {popup.navLinks.map(([label, href]) => (
          <a key={href} href={href}>
            {label}
          </a>
        ))}
      </nav>
    </div>
  );
}

function FormPopup({ popup }) {
  return (
    <div className="modal">
      <h2>{popup.title}</h2>
      {(popup.fields ?? []).map((field) =>
        field.type === 'textarea' ? (
          <textarea key={field.placeholder} placeholder={field.placeholder} />
        ) : (
          <input
            key={field.placeholder}
            type="text"
            placeholder={field.placeholder}
          />
        )
      )}
      {(popup.priceRows ?? []).map(([label, price]) => (
        <div className="price-row" key={label}>
          <span>{label}</span>
          <span>{price}</span>
        </div>
      ))}
      {popup.submit ? <div className="submit">{popup.submit}</div> : null}
      {popup.hint ? <div className="hint">{popup.hint}</div> : null}
    </div>
  );
}

function NotFound({ variant }) {
  return (
    <div className={`page popup-page theme-${variant} popup-notfound`}>
      <Band>
        <div className="modal-wrap">
          <div className="modal notfound-modal">
            <h2>Попап не найден</h2>
            <Link className="btn btn-outlined" to={`/${variant}`}>
              На главную
            </Link>
          </div>
        </div>
      </Band>
    </div>
  );
}

export default function PopupPage() {
  const { variant, popupId } = useParams();

  if (!POPUP_IDS.includes(popupId)) {
    return <NotFound variant={variant} />;
  }

  const popup = POPUPS[popupId];

  return (
    <div className={`page popup-page theme-${variant}`}>
      <Band>
        <div className="modal-wrap">
          <div className="caption">{popup.caption}</div>
          {popup.menu ? <MenuPopup popup={popup} /> : <FormPopup popup={popup} />}
        </div>
      </Band>
    </div>
  );
}
