(function(){
  function getCookie(name){
    const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return v ? v.pop() : '';
  }
  const drop = document.getElementById('dropzone');
  const input = document.getElementById('id_ficheiro');
  const preview = document.getElementById('preview');
  if(!drop || !input) return;
  const MAX_MB = 10; // limite básico
  const allowed = ['image/png','image/jpeg','application/pdf'];

  function showPreview(file){
    if(!preview) return;
    preview.innerHTML = '';
    if(file.type.startsWith('image/')){
      const img = document.createElement('img');
      img.style.maxWidth = '200px';
      img.style.borderRadius = '8px';
      img.src = URL.createObjectURL(file);
      preview.appendChild(img);
    } else {
      const p = document.createElement('div');
      p.textContent = file.name + ' (' + Math.round(file.size/1024) + ' KB)';
      preview.appendChild(p);
    }
  }

  function validate(file){
    if(file.size > MAX_MB*1024*1024){
      alert('Ficheiro acima de ' + MAX_MB + 'MB.');
      return false;
    }
    if(!allowed.includes(file.type)){
      alert('Tipo não permitido. Aceites: PNG, JPEG, PDF.');
      return false;
    }
    return true;
  }

  ;['dragenter','dragover','dragleave','drop'].forEach(e=>{
    drop.addEventListener(e, ev=>{ev.preventDefault();ev.stopPropagation();});
  });
  ;['dragenter','dragover'].forEach(e=>{
    drop.addEventListener(e,()=>drop.classList.add('is-over'));
  });
  ;['dragleave','drop'].forEach(e=>{
    drop.addEventListener(e,()=>drop.classList.remove('is-over'));
  });
  drop.addEventListener('drop', (ev)=>{
    const files = ev.dataTransfer.files;
    if(files && files.length){
      const f = files[0];
      if(!validate(f)) return;
      showPreview(f);
      input.files = files;
      const form = document.getElementById('anexo-form');
      if(form){ form.submit(); }
    }
  });

  input.addEventListener('change', ()=>{
    if(input.files && input.files.length){
      const f = input.files[0];
      if(!validate(f)) { input.value=''; return; }
      showPreview(f);
    }
  });
})();
