function rng(x,y){var r=[];for(var i=x;i<=y;i++)r.push(i);return r}
function mapStr(m){var k=Object.keys(m);return '{'+k.map(function(x){return x+':'+m[x]}).join(', ')+'}'}
var SIM={
two:function(){var a=[1,3,4,6,8,11],t=10,S=[],l=0,r=a.length-1;
 while(l<r){var s=a[l]+a[r];
  if(s===t){S.push({a:a,ptr:{l:l,r:r},ok:[l,r],note:a[l]+' + '+a[r]+' = '+s+' equals the target '+t+'. Found the pair at indices '+l+' and '+r+'.'});break}
  if(s<t){S.push({a:a,ptr:{l:l,r:r},note:a[l]+' + '+a[r]+' = '+s+' is smaller than '+t+'. The sum must grow, so move l right (a[l] can never pair with anything smaller than a[r]).'});l++}
  else{S.push({a:a,ptr:{l:l,r:r},note:a[l]+' + '+a[r]+' = '+s+' is bigger than '+t+'. The sum must shrink, so move r left (a[r] is too large for every remaining partner).'});r--}}
 S.unshift({a:a,ptr:{l:0,r:a.length-1},note:'Sorted array, target '+t+'. Put one pointer at each end.'});return S},
fixed:function(){var a=[2,1,5,1,3,2],k=3,S=[],sum=0;for(var i=0;i<k;i++)sum+=a[i];var best=sum;
 S.push({a:a,ptr:{},hi:rng(0,k-1),note:'First window of size '+k+': sum = '+sum+'. Best so far = '+best+'.'});
 for(i=k;i<a.length;i++){sum+=a[i]-a[i-k];best=Math.max(best,sum);S.push({a:a,ptr:{i:i},hi:rng(i-k+1,i),note:'Slide: add '+a[i]+', drop '+a[i-k]+' → sum = '+sum+'. Best so far = '+best+'. (One add and one subtract, not a re-sum.)'})}
 S.push({a:a,ptr:{},ok:[2,3,4],note:'Maximum window sum of size '+k+' is '+best+'.'});return S},
variable:function(){var s='abcabcbb'.split(''),S=[],l=0,c={},best=0,bl=0;
 for(var r=0;r<s.length;r++){var ch=s[r];c[ch]=(c[ch]||0)+1;
  S.push({a:s,ptr:{l:l,r:r},hi:rng(l,r),note:"Expand: add '"+ch+"' at r="+r+'.'+(c[ch]>1?" '"+ch+"' now appears twice, so the window is invalid.":' Window "'+s.slice(l,r+1).join('')+'" is valid.')});
  while(c[ch]>1){c[s[l]]--;l++;S.push({a:s,ptr:{l:l,r:r},hi:rng(l,r),note:'Shrink: drop the left character, l becomes '+l+'. Window "'+s.slice(l,r+1).join('')+'".'})}
  if(r-l+1>best){best=r-l+1;bl=l}}
 S.push({a:s,ptr:{},ok:rng(bl,bl+best-1),note:'Longest substring without repeats has length '+best+'. Each index entered and left the window once, so O(n).'});return S},
prefix:function(){var a=[3,4,7,2,-3,1,4,2],k=7,S=[],m={0:1},sum=0,cnt=0;
 S.push({a:a,ptr:{},note:'Count subarrays with sum = '+k+'. Seed the map with {0:1} (the empty prefix).'});
 for(var i=0;i<a.length;i++){sum+=a[i];var need=sum-k,add=m[need]||0;cnt+=add;m[sum]=(m[sum]||0)+1;
  S.push({a:a,ptr:{i:i},ok:add?[i]:[],note:'Prefix sum = '+sum+'. Need an earlier prefix of '+sum+' − '+k+' = '+need+': seen '+add+' time(s), so '+add+' subarray(s) end here. Total = '+cnt+'. Map = '+mapStr(m)})}
 return S},
kadane:function(){var a=[-2,1,-3,4,-1,2,1,-5,4],S=[],cur=a[0],st=0,best=a[0],bs=0,be=0;
 S.push({a:a,ptr:{i:0},hi:[0],ok:[0],note:'Start: cur = '+cur+', best = '+best+'.'});
 for(var i=1;i<a.length;i++){var restart=a[i]>cur+a[i];
  if(restart){cur=a[i];st=i}else{cur+=a[i]}
  if(cur>best){best=cur;bs=st;be=i}
  S.push({a:a,ptr:{i:i},hi:rng(st,i),ok:rng(bs,be),note:(restart?'The running sum was negative, so restart at index '+i+': cur = '+cur+'.':'Extend the run: cur = '+cur+'.')+' best = '+best+' (green).'})}
 return S},
hash:function(){var a=[5,1,9,3,7],t=12,S=[],m={};S.push({a:a,ptr:{},note:'Find two numbers that sum to '+t+'. Keep a map value → index of what we have already seen.'});
 for(var i=0;i<a.length;i++){var need=t-a[i];
  if(need in m){S.push({a:a,ptr:{i:i},ok:[m[need],i],note:'Need '+need+' for '+a[i]+': it is in the map at index '+m[need]+'. Answer = ['+m[need]+', '+i+'].'});break}
  m[a[i]]=i;S.push({a:a,ptr:{i:i},note:'At '+a[i]+': need '+need+', not seen yet. Store '+a[i]+' → '+i+'. Map = '+mapStr(m)})}
 return S},
dutch:function(){var a=[2,0,2,1,1,0],S=[],lo=0,mid=0,hi=a.length-1;
 function p(n,ok){S.push({a:a.slice(),ptr:{lo:lo,mid:mid,hi:hi},ok:ok||[],note:n})}
 p('lo marks the end of the 0s, hi the start of the 2s, mid scans the unknown middle.');
 while(mid<=hi){var v=a[mid];
  if(v===0){a[mid]=a[lo];a[lo]=0;lo++;mid++;p('a[mid] was 0: swap into the 0-zone, advance lo and mid.')}
  else if(v===2){a[mid]=a[hi];a[hi]=2;hi--;p('a[mid] was 2: swap with a[hi], shrink hi. Do NOT advance mid; the swapped-in value is unexamined.')}
  else{mid++;p('a[mid] is 1: it already belongs in the middle zone, advance mid.')}}
 S.push({a:a.slice(),ptr:{},ok:rng(0,a.length-1),note:'mid passed hi: sorted in one pass, O(n), O(1) space.'});return S},
binary:function(){var a=[1,3,5,7,7,7,9,11],t=7,S=[],lo=0,hi=a.length-1;
 S.push({a:a,ptr:{lo:lo,hi:hi},note:'Find the FIRST index with a[i] ≥ '+t+' (lower bound). Invariant: the answer is always inside [lo, hi].'});
 while(lo<hi){var mid=lo+((hi-lo)>>1);
  if(a[mid]>=t){S.push({a:a,ptr:{lo:lo,mid:mid,hi:hi},hi:rng(lo,hi),note:'mid = '+mid+', a[mid] = '+a[mid]+' ≥ '+t+'. mid could be the answer, so keep it: hi = mid.'});hi=mid}
  else{S.push({a:a,ptr:{lo:lo,mid:mid,hi:hi},hi:rng(lo,hi),note:'mid = '+mid+', a[mid] = '+a[mid]+' < '+t+'. Everything up to mid is too small: lo = mid + 1.'});lo=mid+1}}
 S.push({a:a,ptr:{lo:lo},ok:[lo],note:'lo = hi = '+lo+'. First occurrence of '+t+' is at index '+lo+'. Each step halved the range: O(log n).'});return S},
rotated:function(){var a=[4,5,6,7,0,1,2],t=0,S=[],lo=0,hi=a.length-1;
 S.push({a:a,ptr:{lo:lo,hi:hi},note:'Sorted array rotated at an unknown point. Search for '+t+'. One half around mid is always sorted.'});
 while(lo<=hi){var mid=lo+((hi-lo)>>1);
  if(a[mid]===t){S.push({a:a,ptr:{lo:lo,mid:mid,hi:hi},ok:[mid],note:'a[mid] = '+t+'. Found at index '+mid+'.'});break}
  if(a[lo]<=a[mid]){var go=a[lo]<=t&&t<a[mid];S.push({a:a,ptr:{lo:lo,mid:mid,hi:hi},hi:rng(lo,mid),note:'Left half ['+lo+'..'+mid+'] is sorted ('+a[lo]+' ≤ '+a[mid]+'). '+t+(go?' lies inside it: hi = mid − 1.':' is not inside it: search the right, lo = mid + 1.')});if(go)hi=mid-1;else lo=mid+1}
  else{var go2=a[mid]<t&&t<=a[hi];S.push({a:a,ptr:{lo:lo,mid:mid,hi:hi},hi:rng(mid,hi),note:'Right half ['+mid+'..'+hi+'] is sorted. '+t+(go2?' lies inside it: lo = mid + 1.':' is not inside it: search the left, hi = mid − 1.')});if(go2)lo=mid+1;else hi=mid-1}}
 return S},
quick:function(){var a=[3,2,1,5,6,4],S=[],target=a.length-2,lo=0,hi=a.length-1;
 function dim(){var d=[];for(var x=0;x<a.length;x++)if(x<lo||x>hi)d.push(x);return d}
 S.push({a:a.slice(),ptr:{},note:'2nd largest = element at sorted index n − k = '+target+'. Partition around a pivot; recurse into ONE side only.'});
 while(lo<=hi){var pv=a[hi],i=lo;
  S.push({a:a.slice(),ptr:{lo:lo,pivot:hi},dim:dim(),hi:[hi],note:'Partition ['+lo+'..'+hi+'] with pivot '+pv+' (last element). i marks where the next smaller element goes.'});
  for(var j=lo;j<hi;j++){if(a[j]<pv){var tm=a[i];a[i]=a[j];a[j]=tm;i++;S.push({a:a.slice(),ptr:{i:i,j:j,pivot:hi},dim:dim(),note:a[i-1]+' < '+pv+': swap into the "smaller" zone, i = '+i+'.'})}
   else S.push({a:a.slice(),ptr:{i:i,j:j,pivot:hi},dim:dim(),note:a[j]+' ≥ '+pv+': leave it, move j on.'})}
  var t2=a[i];a[i]=a[hi];a[hi]=t2;
  if(i===target){S.push({a:a.slice(),ptr:{p:i},ok:[i],dim:dim(),note:'Pivot lands at index '+i+' = target index. Answer: '+a[i]+'.'});break}
  S.push({a:a.slice(),ptr:{p:i},ok:[i],dim:dim(),note:'Pivot '+pv+' is now at its final sorted index '+i+(i<target?' < target '+target+': only the right side can contain it.':' > target '+target+': only the left side can contain it.')});
  if(i<target)lo=i+1;else hi=i-1}
 return S},
amort:function(){var S=[],cap=1,n=0,a=[''],cost=0;
 S.push({a:a.slice(),ptr:{},note:'A dynamic array starts with capacity 1. Append 1..8. When it is full, allocate double the space and copy everything over.'});
 for(var v=1;v<=8;v++){
  if(n===cap){var c=n;cap*=2;var b=[];for(var i=0;i<cap;i++)b.push(i<n?a[i]:'');cost+=c;a=b;S.push({a:a.slice(),ptr:{},hi:rng(0,n-1),note:'Full. Resize to capacity '+cap+': copy '+c+' element(s). Total copy cost so far = '+cost+'.'})}
  a[n]=v;n++;S.push({a:a.slice(),ptr:{i:n-1},ok:[n-1],note:'Append '+v+' (cost 1). Length '+n+', capacity '+cap+'.'})}
 S.push({a:a.slice(),ptr:{},note:'8 appends cost 8 writes + '+cost+' copies = '+(8+cost)+' units, under 2 per append. Rare expensive steps are paid for by many cheap ones: amortised O(1).'});return S},
pairs:function(){var a=['a','b','c','d','e'],S=[],k=0;
 S.push({a:a,ptr:{},note:'Nested loop: for every i, for every j > i. Count how many (i, j) pairs get visited.'});
 for(var i=0;i<a.length;i++)for(var j=i+1;j<a.length;j++){k++;S.push({a:a,ptr:{i:i,j:j},hi:[i,j],note:'Pair #'+k+': ('+a[i]+', '+a[j]+').'})}
 S.push({a:a,ptr:{},ok:rng(0,a.length-1),note:'n = 5 gave '+k+' pairs = n(n−1)/2. Double n and the work roughly quadruples: O(n²).'});return S},
anagram:function(){var s='listen',t='silent',a=s.split('').concat(t.split('')),S=[],c={};
 function A(){return {label:'counts',items:Object.keys(c).map(function(k){return k+': '+c[k]})}}
 S.push({a:a,ptr:{},note:'Are "listen" and "silent" anagrams? Count the letters of the first word UP and the second word DOWN.'});
 for(var i=0;i<s.length;i++){c[s[i]]=(c[s[i]]||0)+1;S.push({a:a,ptr:{i:i},hi:[i],aux:A(),note:"First word: +1 for '"+s[i]+"'."})}
 for(var j=0;j<t.length;j++){var k=s.length+j;c[t[j]]=(c[t[j]]||0)-1;S.push({a:a,ptr:{j:k},hi:[k],aux:A(),note:"Second word: −1 for '"+t[j]+"'."+(c[t[j]]<0?' The count went negative, so it is not an anagram.':'')})}
 S.push({a:a,ptr:{},ok:rng(0,a.length-1),aux:A(),note:'Every count is back to 0, so they are anagrams. O(n) time and O(1) space (26 letters).'});return S},
palin:function(){var s='a.b,.B.a'.split(''),S=[],l=0,r=s.length-1;
 function al(c){return /[a-z0-9]/i.test(c)}
 S.push({a:s,ptr:{l:l,r:r},note:'Valid palindrome, ignoring case and punctuation. One pointer at each end.'});
 while(l<r){
  if(!al(s[l])){S.push({a:s,ptr:{l:l,r:r},dim:[l],note:"'"+s[l]+"' is not a letter or digit: skip it (l++)."});l++;continue}
  if(!al(s[r])){S.push({a:s,ptr:{l:l,r:r},dim:[r],note:"'"+s[r]+"' is not a letter or digit: skip it (r--)."});r--;continue}
  var eq=s[l].toLowerCase()===s[r].toLowerCase();
  S.push({a:s,ptr:{l:l,r:r},hi:[l,r],ok:eq?[l,r]:[],note:"Compare '"+s[l]+"' and '"+s[r]+"' ignoring case: "+(eq?'match, move both inward.':'mismatch, so it is NOT a palindrome.')});
  if(!eq)return S;l++;r--}
 S.push({a:s,ptr:{},ok:rng(0,s.length-1),note:'The pointers met without a mismatch: palindrome. O(n) time, O(1) space.'});return S},
center:function(){var s='babad'.split(''),S=[],bl=0,bestLen=0;
 function tryC(l,r,kind){var any=false;
  while(l>=0&&r<s.length&&s[l]===s[r]){any=true;var len=r-l+1;if(len>bestLen){bestLen=len;bl=l}
   S.push({a:s,ptr:{l:l,r:r},hi:rng(l,r),ok:bestLen?rng(bl,bl+bestLen-1):[],note:kind+' centre: "'+s.slice(l,r+1).join('')+'" is a palindrome (length '+len+'). Best so far: '+bestLen+'. Expand outward.'});l--;r++}
  S.push({a:s,ptr:{},ok:bestLen?rng(bl,bl+bestLen-1):[],note:kind+' centre: '+(any?'cannot expand further (mismatch or edge).':'the two sides differ immediately, nothing to expand.')})}
 S.push({a:s,ptr:{},note:'Every palindrome mirrors around a centre: a letter (odd length) or a gap (even length). Try all 2n−1 centres and expand while both sides match.'});
 for(var i=0;i<s.length;i++){tryC(i,i,'Odd (index '+i+')');if(i<s.length-1)tryC(i,i+1,'Even (gap after '+i+')')}
 S.push({a:s,ptr:{},ok:rng(bl,bl+bestLen-1),note:'Longest palindromic substring: "'+s.slice(bl,bl+bestLen).join('')+'" (length '+bestLen+'; "aba" ties). 2n−1 centres × O(n) expansion = O(n²) time, O(1) space.'});return S},
minwin:function(){var s='ADOBECODEBANC'.split(''),S=[],need={A:1,B:1,C:1},have={},formed=0,req=3,l=0,best=1e9,bl=0;
 function A(){return {label:'covered '+formed+' / '+req,items:['A','B','C'].map(function(k){return k+' '+(have[k]||0)+'/1'})}}
 S.push({a:s,ptr:{l:0,r:0},aux:A(),note:'Smallest window of the string that contains A, B and C. Expand r; once the window covers everything, shrink l as far as possible.'});
 for(var r=0;r<s.length;r++){var c=s[r];if(need[c]){have[c]=(have[c]||0)+1;if(have[c]===need[c])formed++}
  S.push({a:s,ptr:{l:l,r:r},hi:rng(l,r),aux:A(),note:"Expand: add '"+c+"'. "+(formed===req?'The window now covers A, B and C.':'Still missing some required letters.')});
  while(formed===req){if(r-l+1<best){best=r-l+1;bl=l}var d=s[l];
   S.push({a:s,ptr:{l:l,r:r},hi:rng(l,r),ok:rng(bl,bl+best-1),aux:A(),note:'Valid window "'+s.slice(l,r+1).join('')+'" (length '+(r-l+1)+'); shortest so far = '+best+'. Try to shrink: drop \''+d+'\' from the left.'});
   if(need[d]){have[d]--;if(have[d]<need[d])formed--}l++}}
 S.push({a:s,ptr:{},ok:rng(bl,bl+best-1),note:'Minimum window: "'+s.slice(bl,bl+best).join('')+'". l and r only move forward, so O(n).'});return S},
kmp:function(){var p='ababaca'.split(''),lps=[0],S=[],len=0,i=1;
 function A(){return {label:'lps (longest border)',items:lps.map(function(v,k){return k+': '+v})}}
 S.push({a:p,ptr:{},aux:A(),note:'lps[i] = length of the longest proper prefix of p[0..i] that is also a suffix of it. lps[0] = 0. KMP uses it to never re-read text.'});
 while(i<p.length){var ii=i,ll=len;
  if(p[i]===p[len]){len++;lps[i]=len;i++;S.push({a:p,ptr:{i:ii,len:ll},hi:[ii,ll],ok:[ii],aux:A(),note:'p['+ii+'] = p['+ll+'] = \''+p[ii]+'\': the border grows, lps['+ii+'] = '+len+'.'})}
  else if(len>0){len=lps[len-1];S.push({a:p,ptr:{i:ii,len:ll},hi:[ii,ll],aux:A(),note:'p['+ii+'] \''+p[ii]+'\' ≠ p['+ll+'] \''+p[ll]+'\'. Fall back to len = lps['+(ll-1)+'] = '+len+' (try a shorter border; never restart from scratch).'})}
  else{lps[i]=0;i++;S.push({a:p,ptr:{i:ii,len:0},hi:[ii],aux:A(),note:'\''+p[ii]+'\' ≠ \''+p[0]+'\' and there is no shorter border: lps['+ii+'] = 0.'})}}
 S.push({a:p,ptr:{},ok:rng(0,p.length-1),aux:A(),note:'lps = ['+lps.join(', ')+']. Built in O(m): len only falls back as far as it has climbed.'});return S},
decode:function(){var s='3[a2[c]]'.split(''),S=[],stack=[],cur='',num=0;
 function A(){return {label:'stack (count, text before)',items:(stack.length?stack.map(function(x){return '('+x[0]+', "'+x[1]+'")'}):['empty']).concat(['cur = "'+cur+'"'])}}
 S.push({a:s,ptr:{},aux:A(),note:'Decode k[text]. Keep a stack: on "[" save (count, text so far); on "]" pop and repeat the inner text.'});
 for(var i=0;i<s.length;i++){var c=s[i],n;
  if(/\d/.test(c)){num=num*10+(+c);n='Digit: repeat count is now '+num+'.'}
  else if(c==='['){stack.push([num,cur]);n='"[": push ('+num+', "'+cur+'") and start a fresh inner string.';num=0;cur=''}
  else if(c===']'){var t=stack.pop();n='"]": pop ('+t[0]+', "'+t[1]+'"). New text = "'+t[1]+'" + "'+cur+'" × '+t[0]+'.';cur=t[1]+cur.repeat(t[0])}
  else{cur+=c;n="Letter '"+c+"': append to the current text."}
  S.push({a:s,ptr:{i:i},hi:[i],aux:A(),note:n})}
 S.push({a:s,ptr:{},ok:rng(0,s.length-1),aux:A(),note:'Result: "'+cur+'". Each character is handled once: O(n + output length).'});return S},
compress:function(){var a='aabbccc'.split(''),S=[],w=0,r=0;
 S.push({a:a.slice(),ptr:{w:0,r:0},note:'Compress runs in place: "aabbccc" → "a2b2c3". r reads groups, w writes the result at the front. w never passes r, so no extra array.'});
 while(r<a.length){var ch=a[r],st=r;while(r<a.length&&a[r]===ch)r++;var cnt=r-st;
  S.push({a:a.slice(),ptr:{w:w,r:st},hi:rng(st,r-1),note:"Group found: '"+ch+"' × "+cnt+'.'});
  a[w++]=ch;if(cnt>1)String(cnt).split('').forEach(function(d){a[w++]=d});
  S.push({a:a.slice(),ptr:{w:w},ok:rng(0,w-1),note:"Write '"+ch+"'"+(cnt>1?' and the count '+cnt:'')+' at the front. Compressed so far: "'+a.slice(0,w).join('')+'".'})}
 S.push({a:a.slice(),ptr:{},ok:rng(0,w-1),dim:rng(w,a.length-1),note:'New length = '+w+' ("'+a.slice(0,w).join('')+'"). Anything after w is ignored. O(n) time, O(1) space.'});return S},
unique:function(){var s='loveleetcode'.split(''),S=[],c={};
 function A(){return {label:'counts',items:Object.keys(c).map(function(k){return k+': '+c[k]})}}
 S.push({a:s,ptr:{},note:'First non-repeating character. Pass 1 counts every letter; pass 2 finds the first letter whose count is 1.'});
 for(var i=0;i<s.length;i++){c[s[i]]=(c[s[i]]||0)+1;S.push({a:s,ptr:{i:i},hi:[i],aux:A(),note:"Pass 1: count '"+s[i]+"'."})}
 for(i=0;i<s.length;i++){if(c[s[i]]===1){S.push({a:s,ptr:{i:i},ok:[i],aux:A(),note:"Pass 2: '"+s[i]+"' has count 1: answer is index "+i+'.'});return S}
  S.push({a:s,ptr:{i:i},dim:[i],aux:A(),note:"Pass 2: '"+s[i]+"' appears "+c[s[i]]+' times, skip it.'})}
 return S}};
